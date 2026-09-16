from dataclasses import dataclass
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')

def _bool(name, default=False):
    return os.getenv(name, str(default)).lower() in {'1','true','yes','on'}

def _int(name, default):
    try: return int(os.getenv(name, str(default)))
    except ValueError: return default

@dataclass(frozen=True)
class Settings:
    root: Path = ROOT
    username: str = os.getenv('X_USERNAME', '')
    email: str = os.getenv('X_EMAIL', '')
    password: str = os.getenv('X_PASSWORD', '')
    cookies_file: Path = ROOT / os.getenv('X_COOKIES_FILE', 'data/cookies.json')
    llm_model: str = os.getenv('LLM_MODEL', 'gpt-5-mini')
    telegram_token: str = os.getenv('TELEGRAM_BOT_TOKEN', '')
    telegram_chat_id: str = os.getenv('TELEGRAM_CHAT_ID', '')
    poll_interval: int = _int('POLL_INTERVAL_SECONDS', 60)
    max_replies_cycle: int = _int('MAX_REPLIES_PER_CYCLE', 5)
    max_replies_author_day: int = _int('MAX_REPLIES_PER_AUTHOR_PER_DAY', 1)
    max_replies_day: int = _int('MAX_REPLIES_PER_DAY', 20)
    min_request_delay: int = _int('MIN_REQUEST_DELAY_SECONDS', 5)
    search_count: int = _int('SEARCH_COUNT', 20)
    max_tweet_age_minutes: int = _int('MAX_TWEET_AGE_MINUTES', 5)
    run_once: bool = _bool('RUN_ONCE', False)
    safe_mode: bool = _bool('SAFE_MODE', True)
    mock_mode: bool = _bool('MOCK_MODE', False)

settings = Settings()
