import aiohttp
async def notify(settings,tweet,reply,status,url=''):
    if not settings.telegram_token or not settings.telegram_chat_id: return
    msg=f'RAVIQO {status}\n\n@{tweet.author}\nTweet:\n"{tweet.text}"\n\nReply:\n"{reply}"\n\nTweet: {tweet.url}\nReply: {url or "not posted (SAFE_MODE)"}'
    async with aiohttp.ClientSession() as s:
        await s.post(f'https://api.telegram.org/bot{settings.telegram_token}/sendMessage',json={'chat_id':settings.telegram_chat_id,'text':msg})
async def error_notify(settings,error):
    if settings.telegram_token and settings.telegram_chat_id:
        async with aiohttp.ClientSession() as s: await s.post(f'https://api.telegram.org/bot{settings.telegram_token}/sendMessage',json={'chat_id':settings.telegram_chat_id,'text':f'RAVIQO ERROR\n{error}'})
