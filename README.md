# RAVIQO X Reply Bot

A safe-by-default, modular X conversation monitor that finds fresh keyword matches, filters sensitive contexts, generates short contextual humor, validates it, logs every decision, and optionally posts replies through Twikit.

## Current integration note

The project uses `twifork[impersonate]==2.4.0`, a maintained drop-in replacement that still imports as `twikit`, fixes the upstream `twikit==2.3.3` `KEY_BYTE` transaction-parser breakage, and uses Chrome TLS impersonation to avoid the Cloudflare 403 encountered by the default HTTP fingerprint. It supports cookie-backed login, `search_tweet(query, 'Latest')`, and `create_tweet(text=..., reply_to=<tweet id>)`. It uses X's unofficial/internal API, so account suspension risk cannot be eliminated. The bot therefore uses `SAFE_MODE=true` by default, conservative request delays, author/day and daily reply caps, duplicate prevention, and no rate-limit bypass. For a production deployment, prefer an official X API product if your account and plan provide the required recent-search and write access.

## Install

```bash
cd raviqo-x-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `OPENAI_API_KEY` and optionally `OPENAI_API_BASE`. The default model is `gpt-5-mini`, selected for fast, cost-aware generation. Add X credentials only when ready. Telegram fields are optional.

## Authenticate and run safely

The bot loads browser-export cookies from `data/cookies.json`; password login is not required. Never commit `.env` or cookies. The first read-only check can be run with `PYTHONPATH=. python tests/check_cookies.py`. For a fully local test without X or LLM credentials:

```bash
MOCK_MODE=true SAFE_MODE=true python main.py
```

This runs continuously. Stop with Ctrl-C. The first cycle creates `data/raviqo.db` and `data/logs.xlsx` and records a `DRY_RUN` reply without posting.

## Enable posting

After reviewing dry-run logs, set `SAFE_MODE=false`. This is an external side effect: use a mature account, start with low caps, and monitor the account manually. The implementation never attempts to bypass X restrictions.

## Configure

Edit `config/keywords.json` to add or remove terms without changing Python. Change `POLL_INTERVAL_SECONDS`, `MAX_REPLIES_PER_CYCLE`, `MAX_REPLIES_PER_AUTHOR_PER_DAY`, `MAX_REPLIES_PER_DAY`, `MIN_REQUEST_DELAY_SECONDS`, and `SEARCH_COUNT` in `.env`. The `MAX_REPLIES_PER_DAY` field is a defense-in-depth cap; the current database query is designed to be extended with a daily global count before production posting.

## Inspect output

`data/logs.xlsx` contains Date, Time, Tweet ID, author, original tweet, URL, age, engagement, keyword, generated reply, status, reply URL, and error. `data/raviqo.db` stores tweets, replies, authors, and errors for duplicate protection and analysis.

## Tests

```bash
pytest -q
python -m py_compile *.py
```

## GitHub Actions every five minutes

The included `.github/workflows/raviqo.yml` runs one cycle every five minutes. It only accepts tweets whose parsed creation time is between **now and five minutes ago**; missing or unparseable timestamps are rejected rather than treated as current. Each run uses `RUN_ONCE=true`, so it searches, processes at most one candidate by default, and exits. The workflow commits `data/raviqo.db` and `data/logs.xlsx` back to the repository so later runs know which tweets have already been processed. GitHub scheduled workflows are best-effort and may start late; the five-minute age gate still prevents old tweets from being posted.

Add these repository secrets: `RAVIQO_COOKIES_JSON` containing the browser-export cookie JSON, `OPENAI_API_KEY`, and optionally `OPENAI_API_BASE`, `TELEGRAM_BOT_TOKEN`, and `TELEGRAM_CHAT_ID`. Keep `data/cookies.json` out of Git. The workflow writes it only during the job and deletes it before committing. Enable the workflow from the Actions tab and use **Run workflow** for a manual test. It is configured with `SAFE_MODE=false` because this is the live posting workflow; use a separate branch or change it to `true` while validating setup.

## Marketing positioning and roast style

The keyword file now covers digital marketing, customer acquisition, lead generation, paid advertising, Meta/Google/TikTok/LinkedIn ads, ROAS/CAC/CPC/CPM, landing pages, CRO, funnels, email marketing, founders, SaaS, ecommerce, agency life, client revisions, and marketing humor. The prompt permits a **light roast of the marketing idea, metric, campaign, or situation** to earn attention, but it prohibits personal abuse, protected-characteristic attacks, serious crises, fabricated claims, and forced jokes. RAVIQO is not inserted into every reply; the objective is to build recognition through sharp, relevant participation rather than repetitive pitching.

## Troubleshooting

If login fails, delete `data/cookies.json`, verify credentials and any 2FA/CAPTCHA requirement, then retry once. If X returns a rate-limit or account-protection error, stop the bot, wait for the reset/cooldown, and do not increase request frequency. If generation fails, set `MOCK_MODE=true` to isolate the X integration and inspect the LLM configuration. If Telegram is not configured, notifications are simply skipped.

## Known limitations

Twikit is unofficial and may break when X changes its internal endpoints. X's official API availability, pricing, and limits vary by plan. Impression metrics and post-performance refresh are not yet implemented. The current monitor uses polling rather than a stream and normalizes missing Twikit timestamps conservatively; production should verify timestamps against the installed Twikit version. Automatic humor cannot guarantee perfect judgment, so safe mode and human review are recommended during rollout.
