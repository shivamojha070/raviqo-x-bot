from dataclasses import dataclass
from datetime import datetime, timezone
import asyncio, json, re
from pathlib import Path

@dataclass
class Tweet:
    id:str; author_id:str; author:str; text:str; created_at:str; likes:int=0; replies:int=0; url:str=''
    @property
    def age_minutes(self):
        try: return max(0,(datetime.now(timezone.utc)-datetime.fromisoformat(self.created_at.replace('Z','+00:00'))).total_seconds()/60)
        except Exception: return 9999

def parse_created_at(value):
    if isinstance(value, datetime):
        return (value if value.tzinfo else value.replace(tzinfo=timezone.utc)).astimezone(timezone.utc).isoformat()
    text = str(value or '').strip()
    for fmt in ('%a %b %d %H:%M:%S %z %Y', '%a %b %d %H:%M:%S +0000 %Y', '%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ'):
        try: return datetime.strptime(text, fmt).astimezone(timezone.utc).isoformat()
        except ValueError: pass
    try: return datetime.fromisoformat(text.replace('Z','+00:00')).astimezone(timezone.utc).isoformat()
    except ValueError: return ''

def load_keywords(path:Path): return json.loads(path.read_text())
def score(t):
    age=t.age_minutes; recency=max(0,100-age*2); engagement=min(20,(t.likes+t.replies)/10); relevance=min(30,sum(w in t.text.lower() for w in ['business','marketing','ads','customer','startup','founder'])*5); return recency+engagement+relevance

def safe_context(text):
    bad=r'\b(suicide|self[- ]harm|tragedy|died|death|cancer|abuse|rape|assault|emergency|hospital|hospitalized)\b'
    return not re.search(bad,text,re.I)

class MockMonitor:
    async def search(self, keywords, count):
        now=datetime.now(timezone.utc).isoformat(); return [Tweet('mock-1','author-1','mockfounder','I spent $5,000 on ads and got two customers.',now,12,3,'https://x.com/mock/status/mock-1')]

class TwikitMonitor:
    def __init__(self, settings): self.s=settings; self.client=None
    async def connect(self):
        from twikit import Client
        self.client=Client('en-US', impersonate='chrome124')
        if self.s.cookies_file.exists(): self.client.load_cookies(str(self.s.cookies_file))
        else:
            await self.client.login(auth_info_1=self.s.username,auth_info_2=self.s.email,password=self.s.password,cookies_file=str(self.s.cookies_file))
    async def search(self, keywords, count):
        out=[]
        for group, terms in keywords.items():
            chunks=[]; current=[]; size=0
            for term in terms:
                piece=f'"{term}"'
                if current and size + len(piece) + 5 > 420:
                    chunks.append(current); current=[]; size=0
                current.append(piece); size += len(piece) + 5
            if current: chunks.append(current)
            for chunk in chunks:
                query=f"({' OR '.join(chunk)}) -is:retweet"
                result=await self.client.search_tweet(query,'Latest',count=count)
                for x in result:
                    uid=getattr(getattr(x,'user',None),'id','unknown'); handle=getattr(getattr(x,'user',None),'screen_name','unknown'); created=parse_created_at(getattr(x,'created_at',''))
                    if not created: continue
                    tweet=Tweet(str(x.id),str(uid),handle,x.text,created,int(getattr(x,'favorite_count',0) or 0),int(getattr(x,'reply_count',0) or 0),f'https://x.com/{handle}/status/{x.id}')
                    if 0 <= tweet.age_minutes <= self.s.max_tweet_age_minutes: out.append(tweet)
                await asyncio.sleep(self.s.min_request_delay)
        return sorted({x.id:x for x in out}.values(),key=score,reverse=True)
