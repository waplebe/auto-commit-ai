#!/usr/bin/env python3
"""
Autonomous AI agent: each day creates ~3 new ideas and improves existing ideas (geometric growth).
Runs on GitHub Actions 8x/day. Free model. OPENROUTER_API_KEY in env or .env.
"""

import os
import random
import re
import subprocess
import sys
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
NEW_IDEA_PROB = 3 / 8  # ~3 new ideas per day when 8 runs
MAX_CONTEXT_CHARS = 5500  # for "improve" prompt


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


def get_existing_ideas() -> list[Path]:
    if not IDEAS_DIR.exists():
        return []
    return sorted([d for d in IDEAS_DIR.iterdir() if d.is_dir()])


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
        if not f.is_file():
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


def write_files(files: list[tuple[str, str]], base_dir: Path) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)
    for rel_path, body in files:
        full = base_dir / rel_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(body, encoding="utf-8", newline="\n")


def git_commit_push(path: Path, message: str) -> bool:
    try:
        subprocess.run(
            ["git", "add", str(path)],
            c=REPO_ROOT,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", message],
            c=REPO_ROOT,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "push"],
            c=REPO_ROOT,
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        out = (e.stderr or e.stdout or b"").decode(errors="ignore")
        if "nothing to commit" in out:
            return True
        print("Git error:", out)
        return False


def do_new_idea() -> bool:
    IDEAS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    subdir = IDEAS_DIR / stamp
    print("Creating new idea...")
    content = ask_ai_new_idea()
    files = parse_files(content)
    if not files:
        fallback = f"main_{stamp.replace('-', '').replace(' ', '_')}.txt"
        files = [(fallback, content[:8000])]
    print(f"Writing {len(files)} files to {subdir}")
    write_files(files, subdir)
    msg = f"New idea: {subdir.name}"
    return git_commit_push(subdir, msg)


def do_improve_idea() -> bool:
    ideas = get_existing_ideas()
    if not ideas:
        print("No ideas yet, creating first idea.")
        return do_new_idea()
    idea_dir = random.choice(ideas)
    print(f"Improving idea: {idea_dir.name}")
    context = gather_idea_context(idea_dir)
    content = ask_ai_improve(idea_dir.name, context)
    files = parse_files(content)
    if not files:
        print("No files in AI response, skipping.")
        return False
    write_files(files, idea_dir)
    msg = f"Improve: {idea_dir.name}"
    return git_commit_push(idea_dir, msg)


def main() -> None:
    ideas = get_existing_ideas()
    do_new = len(ideas) == 0 or random.random() < NEW_IDEA_PROB
    if do_new:
        ok = do_new_idea()
    else:
        ok = do_improve_idea()
    print("Done." if ok else "Failed.")


if __name__ == "__main__":
    main()
