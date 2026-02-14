# Auto-commit AI (autonomous agent on GitHub)

This repo is maintained by an **autonomous AI agent** that runs on **GitHub Actions** (free model, no PC needed).

## How it works

- **8 runs per day** (every 3 hours UTC).
- **~3 new ideas per day:** each “new” run creates a small project in `ideas/YYYY-MM-DD_HHMM/` (CLI tool, widget, script, etc.).
- **~5 improvements per day:** each “improve” run picks an existing idea, reads its code, and commits an improvement (new feature, test, refactor, better README). Same idea can be improved again and again.
- **Result:** the repo grows in a geometric way—new ideas plus steady improvements to previous ones.

All automatic; no local setup after you add the API key.

## One-time setup

1. **Get an Open Router API key** (free): [openrouter.ai](https://openrouter.ai) → Keys.

2. **Add it as a repo secret:**
   - Repo → **Settings** → **Secrets and variables** → **Actions**
   - **New repository secret** → Name: `OPENROUTER_API_KEY`, Value: your key

3. **Push this repo to GitHub.** The workflow runs on the schedule; you can also trigger it from **Actions** → **Auto-commit AI** → **Run workflow**.

## Local run (optional)

```bash
pip install -r requirements.txt
# .env: OPENROUTER_API_KEY=sk-or-v1-...
python auto_commit_ai.py
```

## Tuning

- **New vs improve ratio:** in `auto_commit_ai.py`, `NEW_IDEA_PROB = 3/8` → ~3 new ideas per day. Change to e.g. `4/8` for more new ideas.
- **Runs per day:** in `.github/workflows/auto-commit-ai.yml`, change the `schedule` cron (e.g. `0 */2 * * *` = every 2 hours).
- **Model:** set secret or env `OPENROUTER_MODEL` (default: `google/gemma-3-4b-it:free`).
