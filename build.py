import os
import json
from openai import OpenAI
from github import Github

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.environ["GROQ_KEY"],
)
gh = Github(os.environ["GH_TOKEN"])
user = gh.get_user()

prompt = os.environ["USER_PROMPT"]
repo_name = os.environ["USER_REPO"]

SYSTEM = """You build websites. Reply with ONLY JSON:
{"files": {"index.html": "<html>", "style.css": "<css>"}}
No markdown, no explanation."""

resp = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "system", "content": SYSTEM},
              {"role": "user", "content": prompt}],
)

text = resp.choices[0].message.content.strip()
if text.startswith("```"):
    text = text.split("```")[1]
    if text.startswith("json"): text = text[4:]

files = json.loads(text.strip())["files"]

try:
    repo = user.get_repo(repo_name)
except Exception:
    repo = user.create_repo(repo_name, private=False, auto_init=True)

for path, content in files.items():
    try:
        existing = repo.get_contents(path)
        repo.update_file(path, f"update {path}", content, existing.sha)
    except Exception:
        repo.create_file(path, f"add {path}", content)

print("Done:", repo.html_url)
