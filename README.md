# Auto-commit AI (autonomous agent on GitHub)

An **autonomous AI agent** runs on GitHub Actions (free model, no PC needed). Each **new idea** becomes a **separate repository**; **improvements** are commits in those repos.

## How it works

- **8 runs per day** (every 3 hours UTC).
- **~3 new ideas per day:** each “new” run creates a **new public repo** under your account (e.g. `idea-2025-02-14-0930`), pushes the generated project there, and appends the repo name to `agent-repos.txt` in this repo.
- **~5 improvements per day:** each “improve” run picks one of the idea repos from the list, clones it, asks the AI to improve the code, and pushes a commit to that repo.

So you get many small repos (one per idea), each improving over time.

## One-time setup

1. **Open Router API key** (free): [openrouter.ai](https://openrouter.ai) → Keys.  
   Add repo secret: **`OPENROUTER_API_KEY`**.

2. **GitHub PAT** (so the agent can create repos and push to them):  
   GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Fine-grained** or **Classic** → create a token with **repo** scope (read/write repos).  
   Add repo secret: **`GH_PAT`** = that token.

3. Push this repo. The workflow runs on the schedule; you can also run it from **Actions** → **Auto-commit AI** → **Run workflow**.

## Repo list

This repo keeps a list of created idea repos in **`agent-repos.txt`** (one name per line). The agent uses it to choose which repo to improve.

## Local run (optional)

Without `GH_PAT` and `REPO_OWNER`, the script falls back to the old behavior: new ideas go into the **`ideas/`** folder in this repo (no new repos).

```bash
pip install -r requirements.txt
# .env: OPENROUTER_API_KEY=..., optionally GH_PAT=..., REPO_OWNER=your-username
python auto_commit_ai.py
```

## Tuning

- **New vs improve:** in `auto_commit_ai.py`, `NEW_IDEA_PROB = 3/8` → ~3 new repos per day.
- **Schedule:** in `.github/workflows/auto-commit-ai.yml`, edit the `schedule` cron.
- **Model:** secret or env **`OPENROUTER_MODEL`** (default: `google/gemma-3-4b-it:free`).
