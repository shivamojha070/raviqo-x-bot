import json
from pathlib import Path
class HumorEngine:
    def __init__(self, settings, history):
        self.settings=settings; self.history=history; self.prompt=Path(settings.root/'prompts/humor_prompt.txt').read_text()
        self.client=None
        if not settings.mock_mode:
            from openai import OpenAI
            self.client=OpenAI()
    def generate(self,tweet):
        if self.settings.mock_mode: return {'selected':'$5k for two customers. Those two better have lifetime warranties.','style':'exaggeration','candidates':[]}
        r=self.client.chat.completions.create(model=self.settings.llm_model,messages=[{'role':'system','content':'Return JSON only.'},{'role':'user','content':self.prompt.replace('{TWEET}',tweet.text).replace('{AUTHOR}',tweet.author)}],response_format={'type':'json_object'},max_completion_tokens=800)
        return json.loads(r.choices[0].message.content)
