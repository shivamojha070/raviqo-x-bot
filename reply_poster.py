class ReplyPoster:
    def __init__(self, settings, monitor):
        self.s = settings
        self.monitor = monitor

    async def post(self, tweet, reply):
        reply = (reply or '').strip()
        if self.s.safe_mode:
            return {'status': 'DRY_RUN', 'url': ''}
        if not reply:
            raise ValueError('Cannot post an empty reply')
        if len(reply) > 280:
            raise ValueError('Reply exceeds 280 characters')
        if not getattr(tweet, 'id', None):
            raise ValueError('Target tweet has no id')
        if self.monitor.client is None:
            raise RuntimeError('X client is not connected')
        is_logged_in = getattr(self.monitor.client, 'is_logged_in', None)
        if is_logged_in is not None and not await is_logged_in():
            raise RuntimeError('X cookies are stale or the session is not authenticated')
        result = await self.monitor.client.create_tweet(
            text=reply,
            reply_to=str(tweet.id),
        )
        reply_id = str(getattr(result, 'id', '') or '')
        if not reply_id:
            raise RuntimeError('X returned no created reply id')
        username = self.s.username or 'i'
        return {
            'status': 'POSTED',
            'url': f'https://x.com/{username}/status/{reply_id}',
            'reply_id': reply_id,
        }
