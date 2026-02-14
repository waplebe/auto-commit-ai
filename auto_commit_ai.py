#!/usr/bin/env python3
"""
Autonomous AI agent: new idea = new GitHub repo; improve = commit into that repo.
~3 new repos per day, ~5 improvements to existing repos. OPENROUTER_API_KEY + GH_PAT (for repo create/push).
"""

import os
import random
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Install: pip install requests python-dotenv")
    sys.exit(1)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not API_KEY:
    print("Set OPENROUTER_API_KEY in .env or environment")
    sys.exit(1)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = os.environ.get("OPENROUTER_MODEL", "google/gemma-3-4b-it:free")
REPO_ROOT = Path(__file__).resolve().parent
IDEAS_DIR = REPO_ROOT / "ideas"
MANIFEST_FILE = REPO_ROOT / "agent-repos.txt"
NEW_IDEA_PROB = 3 / 8
MAX_CONTEXT_CHARS = 5500

REPO_OWNER = os.environ.get("REPO_OWNER", "").strip()
GH_PAT = os.environ.get("GH_PAT", "").strip()
USE_SEPARATE_REPOS = bool(REPO_OWNER and GH_PAT)


def call_ai(messages: list, max_tokens: int = 4096, temperature: float = 0.85) -> str:
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com",
    }
    r = requests.post(OPENROUTER_URL, json=payload, headers=headers, timeout=120)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def parse_files(content: str) -> list[tuple[str, str]]:
    pattern = re.compile(r"---FILE:\s*([^\n]+)\s*---\s*\n(.*?)(?=---END---|---FILE:|\Z)", re.DOTALL)
    files = []
    for m in pattern.finditer(content):
        path = m.group(1).strip().replace("\\", "/").lstrip("/")
        body = m.group(2).rstrip()
        if path and (body or path.endswith(".md")):
            files.append((path, body))
    return files


def write_files(files: list[tuple[str, str]], base_dir: Path) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    for rel_path, body in files:
        full = base_dir / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(body, encoding="utf-8", newline="\n")


def get_idea_repos_from_manifest() -> list[str]:
    if not MANIFEST_FILE.exists():
        return []
    return [line.strip() for line in MANIFEST_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]


def append_to_manifest(repo_name: str) -> None:
    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_FILE, "a", encoding="utf-8") as f:
        f.write(repo_name + "\n")


def git_push_in_dir(repo_dir: Path, message: str) -> bool:
    """Add all, commit, push in repo_dir (origin already set by clone)."""
    try:
        subprocess.run(["git", "add", "-A"], c=repo_dir, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", message], c=repo_dir, check=True, capture_output=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], c=repo_dir, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print("Git push error:", (e.stderr or e.stdout or b"").decode(errors="ignore"))
        return False


def do_new_idea_separate_repo() -> bool:
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    repo_name = f"idea-{stamp}"
    full_name = f"{REPO_OWNER}/{repo_name}"
    print("Creating new idea repo:", full_name)
    content = ask_ai_new_idea()
    files = parse_files(content)
    if not files:
        fallback = f"main_{stamp.replace('-', '')}.txt"
        files = [(fallback, content[:8000])]
    env = os.environ.copy()
    env["GH_TOKEN"] = GH_PAT
    try:
        subprocess.run(
            ["gh", "repo", "create", full_name, "--public", "--description", f"AI idea {stamp}"],
            env=env,
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        print("gh repo create failed:", (e.stderr or e.stdout or b"").decode(errors="ignore"))
        return False
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        clone_url = f"https://x-access-token:{GH_PAT}@github.com/{full_name}.git"
        subprocess.run(["git", "clone", clone_url, str(tmp_path)], check=True, capture_output=True)
        write_files(files, tmp_path)
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], c=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], c=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "checkout", "-b", "main"], c=tmp_path, capture_output=True)
        if not git_push_in_dir(tmp_path, f"Initial: {repo_name}"):
            return False
    append_to_manifest(repo_name)
    try:
        subprocess.run(["git", "add", str(MANIFEST_FILE)], c=REPO_ROOT, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"Agent: add repo {repo_name}"], c=REPO_ROOT, check=True, capture_output=True)
        subprocess.run(["git", "push"], c=REPO_ROOT, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        if "nothing to commit" not in (e.stderr or b"").decode(errors="ignore"):
            print("Main repo push error:", (e.stderr or e.stdout or b"").decode(errors="ignore"))
    return True


def do_improve_separate_repo() -> bool:
    repos = get_idea_repos_from_manifest()
    if not repos:
        print("No idea repos yet, creating first.")
        return do_new_idea_separate_repo()
    repo_name = random.choice(repos)
    full_name = f"{REPO_OWNER}/{repo_name}"
    print("Improving repo:", full_name)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        clone_url = f"https://x-access-token:{GH_PAT}@github.com/{full_name}.git"
        try:
            subprocess.run(["git", "clone", clone_url, str(tmp_path)], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print("Clone failed:", (e.stderr or e.stdout or b"").decode(errors="ignore"))
            return False
        context = gather_idea_context(tmp_path)
        content = ask_ai_improve(repo_name, context)
        files = parse_files(content)
        if not files:
            print("No files in AI response.")
            return False
        write_files(files, tmp_path)
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], c=tmp_path, check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], c=tmp_path, check=True, capture_output=True)
        return git_push_in_dir(tmp_path, f"Improve: {repo_name}")


def ask_ai_new_idea() -> str:
    prompt = """You are a programmer. Create ONE small, concrete project idea and generate its initial code.

Rules:
- Output ONLY the project. No commentary. Start with ---FILE:
- Use this format for each file:
---FILE: path/within/project/filename.extension---
content
---END---
- Create 2-5 files: at least one code file (Python/JS/HTML/Go etc.) and optionally README.md.
- Pick a clear, useful idea: tiny CLI tool, small web widget, mini script, micro utility. Be creative but keep it small and runnable.
- Code must be self-contained. No "your-api-key" placeholders.
- Start directly with ---FILE:"""
    return call_ai([{"role": "user", "content": prompt}])


def gather_idea_context(idea_dir: Path) -> str:
    parts = []
    total = 0
    for f in sorted(idea_dir.rglob("*")):
        if not f.is_file() or ".git" in f.parts:
            continue
        rel = f.relative_to(idea_dir)
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if total + len(text) + 200 > MAX_CONTEXT_CHARS:
            text = text[: max(0, MAX_CONTEXT_CHARS - total - 200)] + "\n... (truncated)"
        parts.append(f"--- {rel} ---\n{text}")
        total += len(text) + 200
        if total >= MAX_CONTEXT_CHARS:
            break
    return "\n\n".join(parts) if parts else "(no files)"


def ask_ai_improve(idea_name: str, context: str) -> str:
    prompt = f"""This is an existing project "{idea_name}". Improve it with one concrete step.

Current files (path and content):
{context}

Your task: add a small feature, fix something, add a test or example, improve README, or refactor. Output ONLY the files you change or add, in this format (paths relative to project root):
---FILE: path/filename---
content (full file content)
---END---

- Output 1-4 files. You can modify existing files (give full new content) or add new files.
- No commentary. Start directly with ---FILE:"""
    return call_ai([{"role": "user", "content": prompt}], max_tokens=4096, temperature=0.8)


def get_existing_ideas() -> list[Path]:
    if not IDEAS_DIR.exists():
        return []
    return sorted([d for d in IDEAS_DIR.iterdir() if d.is_dir()])


def git_commit_push(path: Path, message: str) -> bool:
    try:
        subprocess.run(["git", "add", str(path)], c=REPO_ROOT, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", message], c=REPO_ROOT, check=True, capture_output=True)
        subprocess.run(["git", "push"], c=REPO_ROOT, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        out = (e.stderr or e.stdout or b"").decode(errors="ignore")
        if "nothing to commit" in out:
            return True
        print("Git error:", out)
        return False


def do_new_idea_in_main_repo() -> bool:
    IDEAS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    subdir = IDEAS_DIR / stamp
    print("Creating new idea (in main repo)...")
    content = ask_ai_new_idea()
    files = parse_files(content)
    if not files:
        fallback = f"main_{stamp.replace('-', '').replace(' ', '_')}.txt"
        files = [(fallback, content[:8000])]
    write_files(files, subdir)
    return git_commit_push(subdir, f"New idea: {subdir.name}")


def do_improve_in_main_repo() -> bool:
    ideas = get_existing_ideas()
    if not ideas:
        return do_new_idea_in_main_repo()
    idea_dir = random.choice(ideas)
    print("Improving idea (in main repo):", idea_dir.name)
    context = gather_idea_context(idea_dir)
    content = ask_ai_improve(idea_dir.name, context)
    files = parse_files(content)
    if not files:
        return False
    write_files(files, idea_dir)
    return git_commit_push(idea_dir, f"Improve: {idea_dir.name}")


def main() -> None:
    if USE_SEPARATE_REPOS:
        do_new = not get_idea_repos_from_manifest() or random.random() < NEW_IDEA_PROB
        ok = do_new_idea_separate_repo() if do_new else do_improve_separate_repo()
    else:
        ideas = get_existing_ideas()
        do_new = len(ideas) == 0 or random.random() < NEW_IDEA_PROB
        ok = do_new_idea_in_main_repo() if do_new else do_improve_in_main_repo()
    print("Done." if ok else "Failed.")


if __name__ == "__main__":
    main()
