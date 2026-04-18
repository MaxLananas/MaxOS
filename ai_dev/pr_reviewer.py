#!/usr/bin/env python3
"""Revieweur automatique de Pull Requests."""

import os, sys, json, time
import urllib.request, urllib.error

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GITHUB_TOKEN   = os.environ.get("GITHUB_TOKEN", "")
REPO_OWNER     = os.environ.get("REPO_OWNER", "MaxLananas")
REPO_NAME      = os.environ.get("REPO_NAME", "MaxOS")
PR_NUMBER      = os.environ.get("PR_NUMBER", "")

if not all([GEMINI_API_KEY, GITHUB_TOKEN, PR_NUMBER]):
    print("Variables manquantes")
    sys.exit(0)

def github(method, endpoint, data=None):
    url     = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/{endpoint}"
    payload = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        url, data=payload,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "MaxOS-AI",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode()
            return json.loads(body) if body else {}
    except Exception as e:
        print(f"[GitHub] {e}")
        return None

def gemini_ask(prompt):
    model = "gemini-2.5-flash-lite"
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + model + ":generateContent?key=" + GEMINI_API_KEY
    )
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 4096, "temperature": 0.1}
    }).encode()
    req = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print(f"[Gemini] {e}")
        return None

def main():
    print(f"[PR Review] PR #{PR_NUMBER}")

    # Récupérer les fichiers modifiés
    files = github("GET", f"pulls/{PR_NUMBER}/files")
    if not files:
        print("[PR Review] Impossible de récupérer les fichiers")
        sys.exit(0)

    # Récupérer les infos de la PR
    pr_info = github("GET", f"pulls/{PR_NUMBER}")
    pr_title = pr_info.get("title", "") if pr_info else ""
    pr_body  = pr_info.get("body", "") if pr_info else ""

    file_list = "\n".join([
        f"- {f.get('filename','?')} (+{f.get('additions',0)} -{f.get('deletions',0)})"
        for f in files[:20]
    ])

    # Patch des changements
    patches = ""
    for f in files[:5]:
        fname = f.get("filename","")
        patch = f.get("patch","")[:1000]
        if patch:
            patches += f"\n--- {fname} ---\n{patch}\n"

    prompt = f"""Tu es un expert OS bare metal x86 qui fait une code review.

Pull Request #{PR_NUMBER} : {pr_title}
Description : {pr_body[:500]}

Fichiers modifies :
{file_list}

Changements (extrait) :
{patches}

Regles du projet MaxOS :
- C pur, pas de librairies standard
- x86 32-bit bare metal
- Pas NULL, size_t, malloc, printf, string.h, stddef.h
- Fonctions existantes a respecter : np_draw, tm_draw, si_draw, ab_draw, etc.

Fais une review professionnelle et concise. Reponds en francais.
Identifie :
1. Les problemes potentiels
2. Les bonnes pratiques respectees
3. Ta recommendation : APPROUVE / CHANGES REQUIS / REJET

Sois direct et professionnel."""

    review = gemini_ask(prompt)
    if not review:
        review = "Impossible d'analyser cette PR automatiquement."

    # Poster le commentaire
    comment_body = f"""## Review automatique par MaxOS AI

{review}

---
*Review generee par MaxOS AI Developer v7.0 ({model if 'model' in dir() else 'Gemini'})*"""

    github("POST", f"issues/{PR_NUMBER}/comments", {"body": comment_body})
    print(f"[PR Review] Commentaire poste sur PR #{PR_NUMBER}")

if __name__ == "__main__":
    main()
