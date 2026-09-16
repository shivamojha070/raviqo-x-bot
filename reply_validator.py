import re
class ReplyValidator:
    def __init__(self, settings): self.settings=settings
    def validate(self, reply, tweet, recent):
        reasons=[]; text=reply.strip()
        source = tweet.text.lower()
        if not text or len(text)>280: reasons.append('empty_or_too_long')
        if len(text.split())<2: reasons.append('too_short')
        if text.lower() in {'this','so true','exactly','100%','😂'}: reasons.append('generic')
        if any(token in source for token in ('marketing','ads','advertising','lead','customer','sales','funnel','conversion','startup','founder','agency','business')):
            greeting_only = ('welcome' in text.lower() or 'congrats' in text.lower() or 'congratulations' in text.lower()) and len(text.split()) < 14
            praise_only = any(token in text.lower() for token in ('great post','love this','well done','keep going'))
            roast_signals = ('but','except','only','still','apparently','somehow','meanwhile','kpi','roi','roas','cac','budget','invoice','spreadsheet','dashboard','burn','paying','working overtime','said nobody','plot twist','tutorial','warranty','lifetime','better have','cost','test','significance','procrastination','a/b','statistically')
            contrast = bool(re.search(r'\b\d+%|\b(expect|unless|until|because|while)\b', text.lower()))
            if greeting_only or praise_only or (not contrast and not any(signal in text.lower() for signal in roast_signals)): reasons.append('not_a_roast')
        if any(x in text.lower() for x in ['dm raviqo','raviqo can help','book a call']): reasons.append('promotional')
        if not any(w in text.lower() for w in tweet.text.lower().split() if len(w)>4):
            # allow punchlines that do not repeat words, but reject obvious unrelated output
            if len(text.split())<4: reasons.append('weak_context')
        for old in recent:
            if old['reply'].lower()==text.lower(): reasons.append('duplicate_reply'); break
        if re.search(r'\b(kill yourself|go die|retard|nigger|faggot)\b',text,re.I): reasons.append('unsafe')
        return not reasons, reasons
