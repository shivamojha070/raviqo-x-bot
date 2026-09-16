import asyncio, logging
from config import settings
from database import Database
from logger import ExcelLogger
from x_monitor import load_keywords, MockMonitor, TwikitMonitor, safe_context
from humor_engine import HumorEngine
from reply_validator import ReplyValidator
from reply_poster import ReplyPoster
from telegram import notify, error_notify

async def run_cycle(monitor, db, log, engine, validator, poster):
    keywords=load_keywords(settings.root/'config/keywords.json')
    tweets=await monitor.search(keywords,settings.search_count); processed=0
    for tweet in tweets:
        if processed>=settings.max_replies_cycle: break
        if tweet.age_minutes > settings.max_tweet_age_minutes: continue
        if db.seen(tweet.id) or db.has_reply_record(tweet.id): continue
        if db.posted_count_today() >= settings.max_replies_day: break
        db.record_tweet(tweet,'multi_group')
        if not safe_context(tweet.text): db.record_reply(tweet.id,'','SENSITIVE'); log.log(tweet,'multi_group',status='SENSITIVE'); continue
        if db.author_count_today(tweet.author_id)>=settings.max_replies_author_day: db.record_reply(tweet.id,'','SKIPPED'); log.log(tweet,'multi_group',status='SKIPPED'); continue
        try:
            result=engine.generate(tweet); reply=result['selected']; ok,reasons=validator.validate(reply,tweet,db.recent_replies())
            if not ok:
                db.record_reply(tweet.id,reply,'LOW_QUALITY',style=result.get('style','')); log.log(tweet,'multi_group',reply,status='LOW_QUALITY',error=','.join(reasons)); continue
            posted=await poster.post(tweet,reply); db.record_reply(tweet.id,reply,posted['status'],posted['url'],result.get('style','')); log.log(tweet,'multi_group',reply,posted['status'],posted['url']); await notify(settings,tweet,reply,posted['status'],posted['url']); processed+=1
            await asyncio.sleep(settings.min_request_delay)
        except Exception as e:
            db.record_error(f'tweet:{tweet.id}',e); log.log(tweet,'multi_group',status='ERROR',error=str(e)); await error_notify(settings,e)
    return processed

async def main():
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    db=Database(settings.root/'data/raviqo.db'); log=ExcelLogger(settings.root/'data/logs.xlsx')
    monitor=MockMonitor() if settings.mock_mode else TwikitMonitor(settings)
    if not settings.mock_mode: await monitor.connect()
    engine=HumorEngine(settings,db); validator=ReplyValidator(settings); poster=ReplyPoster(settings,monitor)
    logging.info('RAVIQO started safe_mode=%s mock_mode=%s',settings.safe_mode,settings.mock_mode)
    while True:
        try: count=await run_cycle(monitor,db,log,engine,validator,poster); logging.info('cycle complete replies=%s',count)
        except Exception as e: logging.exception('cycle failed'); db.record_error('cycle',e); await error_notify(settings,e)
        if settings.run_once: break
        await asyncio.sleep(settings.poll_interval)

if __name__=='__main__': asyncio.run(main())
