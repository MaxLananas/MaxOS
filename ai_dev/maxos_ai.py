#!/usr/bin/env python3

import os, sys, json, time, subprocess, re, hashlib, traceback, random, socket
import urllib.request, urllib.error
from datetime import datetime, timezone

VERSION    = "15.0"
DEBUG      = os.environ.get("MAXOS_DEBUG", "0") == "1"
START_TIME = time.time()
MAX_RUNTIME = 3300

REPO_OWNER = os.environ.get("REPO_OWNER", "MaxLananas")
REPO_NAME  = os.environ.get("REPO_NAME",  "MaxOS")
REPO_PATH  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GH_TOKEN   = os.environ.get("GH_PAT", "") or os.environ.get("GITHUB_TOKEN", "")
DISCORD_WH = os.environ.get("DISCORD_WEBHOOK", "")

GEMINI_MODELS = [
    "gemini-2.5-flash-preview-04-17",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

OPENROUTER_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "qwen/qwen-2.5-coder-32b-instruct:free",
    "deepseek/deepseek-r1-distill-llama-70b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "microsoft/phi-4-reasoning:free",
    "deepseek/deepseek-r1:free",
]

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
]

MISTRAL_MODELS = [
    "mistral-small-latest",
    "open-mistral-7b",
    "open-mixtral-8x7b",
]

def _find_keys(prefix):
    keys = []
    for suffix in [""] + [f"_{i}" for i in range(2, 10)]:
        v = os.environ.get(f"{prefix}{suffix}", "").strip()
        if len(v) >= 8:
            keys.append(v)
    return keys

def _prov(ptype, pid, key, model, url):
    return dict(
        type=ptype, id=pid, key=key, model=model, url=url,
        cooldown=0.0, errors=0, calls=0, tokens=0,
        dead=False, last_ok=0.0, response_times=[],
        consec_429=0
    )

def load_providers():
    pools = []

    gem_keys = _find_keys("GEMINI_API_KEY")
    print(f"  [load] GEMINI     : {len(gem_keys)} clé(s) × {len(GEMINI_MODELS)} modèles")
    gem = []
    for i, key in enumerate(gem_keys, 1):
        for m in GEMINI_MODELS:
            base = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
            pid  = f"gm{i}_{m.replace('gemini-','').replace('-','').replace('.','')[:12]}"
            gem.append(_prov("gemini", pid, key, m, f"{base}?key={key}"))
    if gem:
        pools.append(gem)

    or_keys = _find_keys("OPENROUTER_KEY")
    print(f"  [load] OPENROUTER : {len(or_keys)} clé(s) × {len(OPENROUTER_MODELS)} modèles")
    orl = []
    for i, key in enumerate(or_keys, 1):
        for m in OPENROUTER_MODELS:
            short = m.split("/")[-1].replace(":free", "")[:14]
            orl.append(_prov("openrouter", f"or{i}_{short}", key, m,
                             "https://openrouter.ai/api/v1/chat/completions"))
    if orl:
        pools.append(orl)

    groq_keys = _find_keys("GROQ_KEY")
    print(f"  [load] GROQ       : {len(groq_keys)} clé(s) × {len(GROQ_MODELS)} modèles")
    gro = []
    for i, key in enumerate(groq_keys, 1):
        for m in GROQ_MODELS:
            gro.append(_prov("groq", f"gr{i}_{m[:14]}", key, m,
                             "https://api.groq.com/openai/v1/chat/completions"))
    if gro:
        pools.append(gro)

    mis_keys = _find_keys("MISTRAL_KEY")
    print(f"  [load] MISTRAL    : {len(mis_keys)} clé(s) × {len(MISTRAL_MODELS)} modèles")
    mis = []
    for i, key in enumerate(mis_keys, 1):
        for m in MISTRAL_MODELS:
            mis.append(_prov("mistral", f"ms{i}_{m[:14]}", key, m,
                             "https://api.mistral.ai/v1/chat/completions"))
    if mis:
        pools.append(mis)

    result  = []
    max_len = max((len(p) for p in pools), default=0)
    for i in range(max_len):
        for pool in pools:
            if i < len(pool):
                result.append(pool[i])
    return result

PROVIDERS = load_providers()
_RR       = 0

GH_RATE      = {"remaining": 5000, "reset": 0}
SOURCE_CACHE = {"hash": None, "data": None}
TASK_METRICS = []
_DISC_BUF    = []
_DISC_LAST   = 0.0
_DISC_INTV   = 12

def ts():
    return datetime.now(timezone.utc).strftime("%H:%M:%S")

def uptime():
    s = int(time.time() - START_TIME)
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def mask(k):
    return (k[:6] + "…" + k[-4:]) if k and len(k) > 10 else "***"

def pbar(pct, w=20):
    pct = max(0, min(100, pct))
    f   = int(w * pct / 100)
    return "█" * f + "░" * (w - f) + f" {pct}%"

ICONS = {
    "INFO": "📋", "WARN": "⚠️ ", "ERROR": "❌",
    "OK":   "✅", "BUILD": "🔨", "GIT": "📦",
    "TIME": "⏱️ ", "AI": "🤖",
}

def log(msg, level="INFO"):
    print(f"[{ts()}] {ICONS.get(level, '📋')} {msg}", flush=True)

def watchdog():
    if time.time() - START_TIME >= MAX_RUNTIME:
        log(f"Watchdog: {MAX_RUNTIME}s atteint | {uptime()}", "WARN")
        disc_now("⏰ Watchdog", f"Arrêt après **{uptime()}**", 0xFFA500)
        return False
    return True

def alive():
    now = time.time()
    return sorted(
        [p for p in PROVIDERS if not p["dead"] and now >= p["cooldown"]],
        key=lambda p: (p["consec_429"], p["cooldown"])
    )

def non_dead():
    return [p for p in PROVIDERS if not p["dead"]]

def prov_summary():
    now  = time.time()
    by   = {}
    for p in PROVIDERS:
        if p["dead"]:
            continue
        t = p["type"]
        by.setdefault(t, [0, 0])
        if now >= p["cooldown"]:
            by[t][0] += 1
        else:
            by[t][1] += 1
    lines = [f"**{t}**: 🟢{v[0]} 🔴{v[1]}" for t, v in sorted(by.items())]
    nd = len(non_dead())
    al = len(alive())
    return f"{al}/{nd} dispo — " + " | ".join(lines)

def avg_rt(p):
    rt = p.get("response_times", [])
    return sum(rt) / len(rt) if rt else 999.0

def penalize(p, secs=None, dead=False):
    if dead:
        p["dead"] = True
        log(f"Provider {p['id']} ({p['type']}) → MORT", "ERROR")
        return
    p["errors"] += 1
    p["consec_429"] += 1
    if secs is None:
        secs = min(20 * (2 ** min(p["errors"] - 1, 3)), 180)
    p["cooldown"] = time.time() + secs
    log(f"Provider {p['id']} → cooldown {int(secs)}s (errs={p['errors']})", "WARN")

def reward(p, elapsed):
    p["errors"]    = max(0, p["errors"] - 1)
    p["consec_429"] = 0
    p["last_ok"]   = time.time()
    rt = p.setdefault("response_times", [])
    rt.append(elapsed)
    if len(rt) > 10:
        rt.pop(0)

def pick():
    global _RR
    al = alive()
    if al:
        _RR = (_RR + 1) % len(al)
        return al[_RR]
    nd = non_dead()
    if not nd:
        log("FATAL: tous les providers sont morts", "ERROR")
        disc_now("💀 Mort totale", "Aucun provider disponible. Arrêt.", 0xFF0000)
        sys.exit(1)
    best = min(nd, key=lambda p: p["cooldown"])
    wait = max(best["cooldown"] - time.time() + 0.3, 0.5)
    wait = min(wait, 90)
    log(f"Tous en cooldown → attente {int(wait)}s → {best['id']}", "TIME")
    time.sleep(wait)
    return best

def _call_gemini(p, prompt, max_tok, timeout):
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tok,
            "temperature":     0.05,
        }
    }).encode("utf-8")
    req = urllib.request.Request(
        p["url"], data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode("utf-8"))
    cands = data.get("candidates", [])
    if not cands:
        return None
    c      = cands[0]
    finish = c.get("finishReason", "STOP")
    if finish in ("SAFETY", "RECITATION"):
        log(f"Gemini bloqué: {finish}", "WARN")
        return None
    parts = c.get("content", {}).get("parts", [])
    texts = [
        pt.get("text", "")
        for pt in parts
        if isinstance(pt, dict) and not pt.get("thought") and pt.get("text")
    ]
    result = "".join(texts).strip()
    return result if result else None

def _call_compat(p, prompt, max_tok, timeout):
    if p["type"] == "groq":
        max_tok = min(max_tok, 8192)
        if len(prompt) > 28000:
            prompt = prompt[:28000] + "\n[TRONQUÉ]"
    payload = json.dumps({
        "model":       p["model"],
        "messages":    [{"role": "user", "content": prompt}],
        "max_tokens":  max_tok,
        "temperature": 0.05,
    }).encode("utf-8")
    headers = {
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {p['key']}",
    }
    if p["type"] == "openrouter":
        headers["HTTP-Referer"] = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
        headers["X-Title"]      = "MaxOS AI Developer"
    req = urllib.request.Request(
        p["url"], data=payload, headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode("utf-8"))
    if "error" in data:
        raise RuntimeError(data["error"].get("message", "error")[:200])
    choices = data.get("choices", [])
    if not choices:
        return None
    content = choices[0].get("message", {}).get("content", "")
    return content.strip() if content else None

def ai_call(prompt, max_tokens=32768, timeout=150, tag="?"):
    if len(prompt) > 52000:
        prompt = prompt[:52000] + "\n[TRONQUÉ]"

    max_att    = min(len(PROVIDERS) * 2, 36)
    last_error = ""

    for attempt in range(1, max_att + 1):
        if not watchdog():
            return None
        p  = pick()
        t0 = time.time()
        log(f"[{tag}] {p['type']}/{p['id']} att={attempt}/{max_att}", "AI")

        try:
            text = (
                _call_gemini(p, prompt, max_tokens, timeout)
                if p["type"] == "gemini"
                else _call_compat(p, prompt, max_tokens, timeout)
            )
            elapsed = round(time.time() - t0, 1)

            if not text or not text.strip():
                log(f"[{tag}] Réponse vide ({p['id']}) {elapsed}s", "WARN")
                penalize(p, 15)
                continue

            est_tk       = len(text) // 4
            p["calls"]  += 1
            p["tokens"] += est_tk
            reward(p, elapsed)
            log(f"[{tag}] ✅ {len(text):,}c {elapsed}s ~{est_tk}tk ({p['type']}/{p['model'][:20]})", "OK")
            return text

        except urllib.error.HTTPError as e:
            elapsed = round(time.time() - t0, 1)
            body    = ""
            try:
                body = e.read().decode("utf-8", errors="replace")[:500]
            except Exception:
                pass
            last_error = f"HTTP {e.code}"
            log(f"[{tag}] HTTP {e.code} ({p['id']}) {elapsed}s", "WARN")
            if DEBUG:
                log(f"  body: {body[:200]}", "WARN")

            if e.code == 429:
                penalize(p)
                al_now = [x for x in alive() if x is not p]
                if not al_now:
                    nd_local = non_dead()
                    if nd_local:
                        nxt  = min(x["cooldown"] for x in nd_local) - time.time()
                        wait = max(min(nxt + 0.5, 25), 1)
                    else:
                        wait = 25
                    log(f"[{tag}] Rien dispo, attente {int(wait)}s", "TIME")
                    time.sleep(wait)

            elif e.code == 403:
                bl = body.lower()
                if any(w in bl for w in ["denied", "banned", "suspended", "not authorized", "no access", "forbidden"]):
                    penalize(p, dead=True)
                else:
                    penalize(p, 240)

            elif e.code == 404:
                penalize(p, dead=True)

            elif e.code == 400:
                log(f"[{tag}] 400 body: {body[:150]}", "WARN")
                penalize(p, 45)

            elif e.code in (500, 502, 503, 504):
                penalize(p, 25)
                time.sleep(3)

            else:
                penalize(p, 15)
                time.sleep(2)

        except (TimeoutError, socket.timeout) as e:
            elapsed = round(time.time() - t0, 1)
            log(f"[{tag}] TIMEOUT {timeout}s ({p['id']})", "WARN")
            last_error = f"timeout {timeout}s"
            penalize(p, 25)

        except urllib.error.URLError as e:
            log(f"[{tag}] URLError ({p['id']}): {e.reason}", "WARN")
            last_error = str(e.reason)[:80]
            penalize(p, 20)
            time.sleep(2)

        except RuntimeError as e:
            log(f"[{tag}] RuntimeError ({p['id']}): {e}", "WARN")
            last_error = str(e)[:80]
            penalize(p, 25)

        except Exception as e:
            log(f"[{tag}] Exception ({p['id']}): {type(e).__name__}: {e}", "ERROR")
            last_error = str(e)[:80]
            if DEBUG:
                traceback.print_exc()
            penalize(p, 12)
            time.sleep(1)

    log(f"[{tag}] ÉCHEC TOTAL {max_att} tentatives. Dernière: {last_error}", "ERROR")
    return None

def _disc_raw(embeds):
    if not DISCORD_WH:
        return False
    payload = json.dumps({
        "username": f"MaxOS AI v{VERSION}",
        "embeds":   embeds[:10],
    }).encode()
    req = urllib.request.Request(
        DISCORD_WH, data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "MaxOS-Bot"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status in (200, 204)
    except Exception as ex:
        log(f"Discord err: {ex}", "WARN")
        return False

def _embed(title, desc, color, fields=None):
    al  = len(alive())
    nd  = len(non_dead())
    tk  = sum(p["tokens"] for p in PROVIDERS)
    ca  = sum(p["calls"]  for p in PROVIDERS)
    cur = alive()[0]["model"][:20] if alive() else "?"
    e   = {
        "title":       str(title)[:256],
        "description": str(desc)[:4096],
        "color":       color,
        "timestamp":   datetime.utcnow().isoformat() + "Z",
        "footer":      {
            "text": f"v{VERSION} | {cur} | {al}/{nd} | up {uptime()} | ~{tk:,}tk | {ca}c | GH:{GH_RATE['remaining']}"
        },
    }
    if fields:
        e["fields"] = [
            {
                "name":   str(f.get("name", ""))[:256],
                "value":  str(f.get("value", "?"))[:1024],
                "inline": bool(f.get("inline", False)),
            }
            for f in fields[:25]
        ]
    return e

def disc_log(title, desc="", color=0x5865F2):
    _DISC_BUF.append((title, desc, color))
    _flush_disc(False)

def _flush_disc(force=True):
    global _DISC_LAST
    now = time.time()
    if not force and now - _DISC_LAST < _DISC_INTV:
        return
    if not _DISC_BUF:
        return
    embeds = []
    while _DISC_BUF and len(embeds) < 10:
        t, d, c = _DISC_BUF.pop(0)
        embeds.append(_embed(t, d, c))
    if embeds:
        _disc_raw(embeds)
        _DISC_LAST = time.time()

def disc_now(title, desc="", color=0x5865F2, fields=None):
    _flush_disc(True)
    _disc_raw([_embed(title, desc, color, fields)])

def gh_api(method, endpoint, data=None, raw_url=None, retry=3):
    if not GH_TOKEN:
        return None
    url     = raw_url or f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/{endpoint}"
    payload = json.dumps(data).encode() if data else None
    for att in range(1, retry + 1):
        req = urllib.request.Request(
            url, data=payload,
            headers={
                "Authorization":        f"Bearer {GH_TOKEN}",
                "Accept":               "application/vnd.github+json",
                "Content-Type":         "application/json",
                "User-Agent":           f"MaxOS-AI/{VERSION}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            method=method
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                rem = r.headers.get("X-RateLimit-Remaining")
                rst = r.headers.get("X-RateLimit-Reset")
                if rem:
                    GH_RATE["remaining"] = int(rem)
                if rst:
                    GH_RATE["reset"] = int(rst)
                if GH_RATE["remaining"] < 50:
                    log(f"GH rate limit critique: {GH_RATE['remaining']}", "WARN")
                body = r.read().decode("utf-8", errors="replace")
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", errors="replace")[:300]
            except Exception:
                pass
            if e.code == 403 and "rate limit" in body.lower():
                wait = max(GH_RATE["reset"] - time.time() + 5, 60)
                log(f"GH rate limit 403 → attente {int(wait)}s", "WARN")
                time.sleep(wait)
                continue
            if e.code in (500, 502, 503, 504) and att < retry:
                time.sleep(4 * att)
                continue
            log(f"GH {method} {endpoint} HTTP {e.code}: {body[:100]}", "WARN")
            return None
        except Exception as ex:
            log(f"GH ex: {ex}", "ERROR")
            if att < retry:
                time.sleep(3)
                continue
            return None
    return None

def gh_open_prs():
    r = gh_api("GET", "pulls?state=open&per_page=20")
    return r if isinstance(r, list) else []

def gh_pr_files(n):
    r = gh_api("GET", f"pulls/{n}/files?per_page=50")
    return r if isinstance(r, list) else []

def gh_pr_reviews(n):
    r = gh_api("GET", f"pulls/{n}/reviews")
    return r if isinstance(r, list) else []

def gh_pr_commits(n):
    r = gh_api("GET", f"pulls/{n}/commits?per_page=30")
    return r if isinstance(r, list) else []

def gh_post_review(n, body, event="COMMENT", comments=None):
    pay = {"body": body, "event": event}
    if comments:
        pay["comments"] = [
            {
                "path":  c["path"],
                "line":  c.get("line", 1),
                "side":  "RIGHT",
                "body":  c["body"],
            }
            for c in comments
            if c.get("path") and c.get("body")
        ]
    return gh_api("POST", f"pulls/{n}/reviews", pay)

def gh_approve_pr(n, body):
    return gh_post_review(n, body, "APPROVE")

def gh_req_changes(n, body, comments=None):
    return gh_post_review(n, body, "REQUEST_CHANGES", comments)

def gh_merge_pr(n, title):
    r = gh_api("PUT", f"pulls/{n}/merge", {
        "commit_title": f"merge: {title} [AI]",
        "merge_method": "squash",
    })
    return bool(r and r.get("merged"))

def gh_open_issues():
    r = gh_api("GET", "issues?state=open&per_page=30&sort=created&direction=desc")
    if not isinstance(r, list):
        return []
    return [i for i in r if not i.get("pull_request")]

def gh_issue_comments(n):
    r = gh_api("GET", f"issues/{n}/comments?per_page=50")
    return r if isinstance(r, list) else []

def gh_issue_timeline(n):
    r = gh_api("GET", f"issues/{n}/timeline?per_page=50")
    return r if isinstance(r, list) else []

def gh_close_issue(n, reason="completed"):
    gh_api("PATCH", f"issues/{n}", {"state": "closed", "state_reason": reason})

def gh_add_labels(n, labels):
    gh_api("POST", f"issues/{n}/labels", {"labels": labels})

def gh_remove_label(n, label):
    gh_api("DELETE", f"issues/{n}/labels/{urllib.request.quote(label)}")

def gh_post_comment(n, body):
    gh_api("POST", f"issues/{n}/comments", {"body": body})

def gh_create_issue(title, body, labels=None):
    pay = {"title": title, "body": body}
    if labels:
        pay["labels"] = labels
    return gh_api("POST", "issues", pay)

def gh_list_labels():
    r = gh_api("GET", "labels?per_page=100")
    return {l["name"]: l for l in (r if isinstance(r, list) else [])}

def gh_ensure_labels(desired):
    ex = gh_list_labels()
    c  = 0
    for name, color in desired.items():
        if name not in ex:
            gh_api("POST", "labels", {
                "name":        name,
                "color":       color,
                "description": f"[AI] {name}",
            })
            c += 1
    if c:
        log(f"Labels: {c} créé(s)")

STANDARD_LABELS = {
    "ai-reviewed":  "0075ca",
    "ai-approved":  "0e8a16",
    "ai-rejected":  "b60205",
    "needs-fix":    "e4e669",
    "bug":          "d73a4a",
    "enhancement":  "a2eeef",
    "question":     "d876e3",
    "stale":        "eeeeee",
    "wontfix":      "ffffff",
    "kernel":       "5319e7",
    "driver":       "1d76db",
    "app":          "0052cc",
    "performance":  "f9d0c4",
    "security":     "e11d48",
    "duplicate":    "cfd3d7",
}

def gh_ensure_milestone(title):
    r = gh_api("GET", "milestones?state=open&per_page=30")
    for m in (r if isinstance(r, list) else []):
        if m.get("title") == title:
            return m.get("number")
    r2 = gh_api("POST", "milestones", {
        "title":       title,
        "description": f"[AI] {title}",
    })
    return r2.get("number") if r2 else None

def gh_assign_ms(issue_num, ms_num):
    if ms_num:
        gh_api("PATCH", f"issues/{issue_num}", {"milestone": ms_num})

def gh_list_releases(n=5):
    r = gh_api("GET", f"releases?per_page={n}")
    return r if isinstance(r, list) else []

def gh_create_release(tag, name, body, pre=False):
    r = gh_api("POST", "releases", {
        "tag_name":   tag,
        "name":       name,
        "body":       body,
        "draft":      False,
        "prerelease": pre,
    })
    return r.get("html_url") if r and "html_url" in r else None

def gh_repo_stats():
    repo  = gh_api("GET", "")
    langs = gh_api("GET", "languages")
    contribs = gh_api("GET", "contributors?per_page=10")
    return {
        "stars":       (repo or {}).get("stargazers_count", 0),
        "forks":       (repo or {}).get("forks_count", 0),
        "watchers":    (repo or {}).get("watchers_count", 0),
        "open_issues": (repo or {}).get("open_issues_count", 0),
        "languages":   langs if isinstance(langs, dict) else {},
        "contributors": len(contribs) if isinstance(contribs, list) else 0,
    }

def gh_compare(base, head):
    r = gh_api("GET", f"compare/{base}...{head}")
    return r if r else {}

def gh_search_issues(query):
    url = f"https://api.github.com/search/issues?q={urllib.request.quote(query)}&per_page=10"
    r   = gh_api("GET", "", raw_url=url)
    return (r or {}).get("items", [])

def git_cmd(args, timeout=60):
    r = subprocess.run(
        ["git"] + args, cwd=REPO_PATH,
        capture_output=True, text=True, timeout=timeout
    )
    return r.returncode == 0, r.stdout, r.stderr

def git_sha(short=True):
    ok, out, _ = git_cmd(["rev-parse", "HEAD"])
    if not ok:
        return ""
    s = out.strip()
    return s[:7] if short else s

def git_push(task_name, files, desc, model):
    if not files:
        return True, None, None
    dirs   = set(f.split("/")[0] for f in files if "/" in f)
    pmap   = {"kernel": "kernel", "drivers": "driver", "boot": "boot", "ui": "ui", "apps": "feat"}
    prefix = next((pmap[d] for d in pmap if d in dirs), "feat")
    fshort = ", ".join(os.path.basename(f) for f in files[:3])
    if len(files) > 3:
        fshort += f" +{len(files)-3}"
    short = f"{prefix}: {task_name[:50]} [{fshort}]"
    msg   = f"{short}\n\nFiles: {', '.join(files)}\nModel: {model}\nArch: x86-32\n\n[skip ci]"
    git_cmd(["add", "-A"])
    ok, out, err = git_cmd(["commit", "-m", msg])
    if not ok:
        if "nothing to commit" in (out + err):
            log("Git: rien à committer")
            return True, None, None
        log(f"Commit KO: {err[:200]}", "ERROR")
        return False, None, None
    sha = git_sha()
    ok2, _, e2 = git_cmd(["push"])
    if not ok2:
        git_cmd(["pull", "--rebase"])
        ok2, _, e2 = git_cmd(["push"])
        if not ok2:
            log(f"Push KO: {e2[:200]}", "ERROR")
            return False, None, None
    log(f"Push OK: {sha}", "GIT")
    return True, sha, short

_ERR_RE = re.compile(
    r"error:|fatal error:|fatal:|undefined reference|cannot find|no such file"
    r"|\*\*\* \[|Error \d+\s*$|FAILED\s*$|nasm:.*error|ld:.*error"
    r"|collect2: error|linker command failed|multiple definition|duplicate symbol"
    r"|identifier expected|expression syntax",
    re.IGNORECASE
)

def parse_errs(log_text):
    seen, u = set(), []
    for line in log_text.split("\n"):
        s = line.strip()
        if s and _ERR_RE.search(s) and s not in seen:
            seen.add(s)
            u.append(s[:130])
    return u[:30]

def make_build():
    subprocess.run(["make", "clean"], cwd=REPO_PATH, capture_output=True, timeout=30)
    t0 = time.time()
    try:
        r = subprocess.run(
            ["make"],
            cwd=REPO_PATH, capture_output=True, text=True, timeout=150
        )
    except subprocess.TimeoutExpired:
        log("Build TIMEOUT 150s", "ERROR")
        return False, "TIMEOUT", ["Build timeout après 150s"]
    el   = round(time.time() - t0, 1)
    ok   = r.returncode == 0
    lt   = r.stdout + r.stderr
    errs = parse_errs(lt)
    log(f"Build {'OK' if ok else f'FAIL ({len(errs)} err)'} {el}s", "BUILD")
    for e in errs[:5]:
        log(f"  >> {e[:110]}", "BUILD")
    if ok:
        disc_log("🔨 Build ✅", f"OK en `{el}s`", 0x00CC44)
    else:
        es = "\n".join(f"`{e[:80]}`" for e in errs[:5])
        disc_log(f"🔨 Build ❌ ({len(errs)} err)", f"`{el}s`\n{es}", 0xFF2200)
    return ok, lt, errs

SKIP_DIRS  = {".git", "build", "__pycache__", ".github", "ai_dev"}
SKIP_FILES = {"screen.h.save"}
SRC_EXTS   = {".c", ".h", ".asm", ".ld"}
ALL_FILES  = [
    "boot/boot.asm", "kernel/kernel_entry.asm", "kernel/kernel.c",
    "drivers/screen.h", "drivers/screen.c", "drivers/keyboard.h", "drivers/keyboard.c",
    "ui/ui.h", "ui/ui.c", "apps/notepad.h", "apps/notepad.c",
    "apps/terminal.h", "apps/terminal.c", "apps/sysinfo.h", "apps/sysinfo.c",
    "apps/about.h", "apps/about.c", "Makefile", "linker.ld",
]

def discover_files():
    found = []
    for root, dirs, files in os.walk(REPO_PATH):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f in SKIP_FILES:
                continue
            ext = os.path.splitext(f)[1]
            if ext in SRC_EXTS or f == "Makefile":
                rel = os.path.relpath(os.path.join(root, f), REPO_PATH).replace("\\", "/")
                found.append(rel)
    return sorted(found)

def read_all(force=False):
    af = sorted(set(ALL_FILES + discover_files()))
    h  = hashlib.md5()
    for f in af:
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            st = os.stat(p)
            h.update(f"{st.st_mtime}:{st.st_size}".encode())
    cur = h.hexdigest()
    if not force and SOURCE_CACHE["hash"] == cur and SOURCE_CACHE["data"]:
        return SOURCE_CACHE["data"]
    src = {}
    for f in af:
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    src[f] = fh.read()
            except Exception:
                src[f] = None
        else:
            src[f] = None
    SOURCE_CACHE["hash"] = cur
    SOURCE_CACHE["data"] = src
    return src

def build_ctx(sources, max_chars=40000):
    ctx  = "=== CODE SOURCE MAXOS ===\n\nFICHIERS:\n"
    for f, c in sources.items():
        ctx += f"  {'[OK]' if c else '[--]'} {f}\n"
    ctx  += "\n"
    used  = len(ctx)
    prio  = [
        "kernel/kernel.c", "kernel/kernel_entry.asm",
        "Makefile", "linker.ld", "drivers/screen.h",
    ]
    done  = set()
    for f in prio:
        c = sources.get(f, "")
        if not c:
            continue
        b = "=" * 48 + f"\nFICHIER: {f}\n" + "=" * 48 + "\n" + c + "\n\n"
        if used + len(b) > max_chars:
            continue
        ctx  += b
        used += len(b)
        done.add(f)
    for f, c in sources.items():
        if f in done or not c:
            continue
        b = "=" * 48 + f"\nFICHIER: {f}\n" + "=" * 48 + "\n" + c + "\n\n"
        if used + len(b) > max_chars:
            ctx += f"[{f} tronqué — {len(c)} chars]\n"
            continue
        ctx  += b
        used += len(b)
    return ctx

def proj_stats(sources):
    return {
        "files": sum(1 for c in sources.values() if c),
        "lines": sum(c.count("\n") for c in sources.values() if c),
        "chars": sum(len(c) for c in sources.values() if c),
    }

def analyze_quality(sources):
    bad_inc = ["stddef.h", "string.h", "stdlib.h", "stdio.h", "stdint.h", "stdbool.h", "stdarg.h"]
    bad_sym = [
        "size_t", "NULL", "bool", "true", "false",
        "uint32_t", "uint8_t", "malloc", "free",
        "memset", "memcpy", "strlen", "printf", "sprintf",
    ]
    viols = []
    cf    = af = 0
    for fname, content in sources.items():
        if not content:
            continue
        if fname.endswith((".c", ".h")):
            cf += 1
            for i, line in enumerate(content.split("\n"), 1):
                s = line.strip()
                if s.startswith(("//", "/*", "*")):
                    continue
                for inc in bad_inc:
                    if f"#include <{inc}>" in line or f'#include "{inc}"' in line:
                        viols.append(f"{fname}:{i} inc:{inc}")
                for sym in bad_sym:
                    if re.search(r"\b" + re.escape(sym) + r"\b", line):
                        viols.append(f"{fname}:{i} sym:{sym}")
                        break
        elif fname.endswith(".asm"):
            af += 1
    score = max(0, 100 - len(viols) * 4)
    return {
        "score":      score,
        "violations": viols[:30],
        "c_files":    cf,
        "asm_files":  af,
    }

FILE_SEP_RE = re.compile(
    r"(?:"
    r"={3,}\s*FILE\s*:\s*([^\s=`]+?)\s*={3,}"
    r"|---\s*FILE\s*:\s*([^\s-`]+?)\s*---"
    r"|```\w*\s*\n?//\s*([^\n]+\.\w+)"
    r")",
    re.IGNORECASE
)
END_SEP_RE = re.compile(
    r"(?:={3,}\s*END\s*FILE\s*={3,}|---\s*END\s*FILE\s*---)",
    re.IGNORECASE
)

def parse_ai_files(resp):
    files  = {}
    to_del = []
    cur    = None
    lines  = []
    in_f   = False

    for line in resp.split("\n"):
        s = line.strip()

        del_m = re.match(r"={3,}\s*DELETE\s*:\s*([^\s=`]+?)\s*={3,}", s, re.IGNORECASE)
        if del_m:
            fn = del_m.group(1).strip()
            if fn:
                to_del.append(fn)
                log(f"DELETE: {fn}")
            continue

        file_m = re.match(
            r"(?:={3,}|---)\s*FILE\s*:\s*[`\"]?([^\s=`\"]+?)[`\"]?\s*(?:={3,}|---)",
            s, re.IGNORECASE
        )
        if file_m:
            if in_f and cur and lines:
                _save_file(files, cur, lines)
            fn = file_m.group(1).strip()
            if fn:
                cur   = fn
                lines = []
                in_f  = True
            continue

        if END_SEP_RE.match(s) and in_f:
            if cur:
                _save_file(files, cur, lines)
            cur   = None
            lines = []
            in_f  = False
            continue

        if in_f:
            lines.append(line)

    if in_f and cur and lines:
        _save_file(files, cur, lines)

    if not files and not to_del:
        log(f"Parse: rien trouvé. Début réponse: {resp[:150]}", "WARN")

    return files, to_del

def _save_file(files, path, lines):
    content = "\n".join(lines).strip()
    for lang in ["```c", "```asm", "```nasm", "```makefile", "```ld", "```bash", "```"]:
        if content.startswith(lang):
            content = content[len(lang):].lstrip("\n")
            break
    if content.endswith("```"):
        content = content[:-3].rstrip("\n")
    content = content.strip()
    if content:
        files[path] = content
        log(f"Parsé: {path} ({len(content):,}c)")

def write_files(files):
    written  = []
    repo_real = os.path.realpath(REPO_PATH)
    for path, content in files.items():
        full = os.path.realpath(os.path.join(REPO_PATH, path))
        if not full.startswith(repo_real + os.sep) and full != repo_real:
            log(f"Path traversal bloqué: {path}", "ERROR")
            continue
        os.makedirs(os.path.dirname(full) if os.path.dirname(full) else REPO_PATH, exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        written.append(path)
        log(f"Écrit: {path}")
    SOURCE_CACHE["hash"] = None
    return written

def del_files(paths):
    deleted  = []
    repo_real = os.path.realpath(REPO_PATH)
    for path in paths:
        full = os.path.realpath(os.path.join(REPO_PATH, path))
        if not full.startswith(repo_real + os.sep):
            log(f"Delete path traversal bloqué: {path}", "ERROR")
            continue
        if os.path.exists(full):
            os.remove(full)
            deleted.append(path)
            log(f"Supprimé: {path}")
    SOURCE_CACHE["hash"] = None
    return deleted

def backup(paths):
    bak = {}
    for p in paths:
        full = os.path.join(REPO_PATH, p)
        if os.path.exists(full):
            with open(full, "r", encoding="utf-8", errors="ignore") as f:
                bak[p] = f.read()
    return bak

def restore(bak):
    for p, c in bak.items():
        full = os.path.join(REPO_PATH, p)
        os.makedirs(os.path.dirname(full) if os.path.dirname(full) else REPO_PATH, exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as f:
            f.write(c)
    if bak:
        log(f"Restauré {len(bak)} fichier(s)")
    SOURCE_CACHE["hash"] = None

OS_MISSION = (
    "MISSION MaxOS: OS bare metal x86 complet (type Win11).\n"
    "ORDRE: IDT+PIC→Timer PIT→Mémoire bitmap→VGA mode13h→Terminal→FAT12→GUI"
)

RULES = """RÈGLES BARE METAL x86 ABSOLUES:
INTERDIT includes: stddef.h string.h stdlib.h stdio.h stdint.h stdbool.h stdarg.h
INTERDIT symboles: size_t NULL bool true false uint32_t uint8_t malloc free memset memcpy strlen printf sprintf
REMPLACE: size_t→unsigned int | NULL→0 | bool→int | true→1 | false→0 | uint32_t→unsigned int
GCC: -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie
ASM NASM: macros %macro INTERDIT pour global/extern — écrire chaque global isr0/isr1/.../isr47 explicitement
LD: ld -m elf_i386 -T linker.ld --oformat binary
kernel_entry.asm: global _stack_top AVANT kernel_main, pile 16KB (resb 16384)
Nouveaux .c → Makefile OBJS += build/fichier.o
ZERO commentaire dans le code
io.h: outb/inb inline — JAMAIS redéfinis dans d'autres fichiers
Fonctions déclarées dans .h doivent être définies dans le .c correspondant"""

def default_plan():
    return {
        "score_actuel": 30,
        "niveau_os":    "Prototype bare metal",
        "fonctionnalites_presentes": ["Boot x86", "VGA texte", "Clavier PS/2", "4 apps"],
        "fonctionnalites_manquantes_critiques": ["IDT", "Timer PIT", "Mémoire", "VGA graphique"],
        "prochaine_milestone": "Kernel stable IDT+Timer",
        "plan_ameliorations": [
            {
                "nom":                  "IDT 256 entrées + PIC 8259 + handlers",
                "priorite":             "CRITIQUE",
                "categorie":            "kernel",
                "fichiers_a_modifier":  ["kernel/kernel.c", "kernel/kernel_entry.asm", "Makefile"],
                "fichiers_a_creer":     ["kernel/io.h", "kernel/idt.h", "kernel/idt.c", "kernel/isr.asm"],
                "fichiers_a_supprimer": [],
                "description": (
                    "io.h: static inline outb(port,val) inb(port). "
                    "idt.h: struct IDTEntry 8 bytes __attribute__((packed)) IDTPtr 6 bytes. "
                    "idt.c: idt_set_gate() PIC remap IRQ0→0x20 outb séquence. "
                    "isr.asm: 48 stubs ÉCRITS EXPLICITEMENT isr0: ... isr1: ... pas de macro %rep. "
                    "kernel_entry.asm: global _stack_top EN PREMIER puis pile resb 16384 puis global kernel_main. "
                    "kernel.c: include io.h idt.h — idt_init() sti() halt loop."
                ),
                "impact_attendu": "OS stable sans triple fault",
                "complexite":     "HAUTE",
            },
            {
                "nom":                  "Timer PIT 8253 100Hz + sleep_ms",
                "priorite":             "CRITIQUE",
                "categorie":            "kernel",
                "fichiers_a_modifier":  ["kernel/kernel.c", "Makefile"],
                "fichiers_a_creer":     ["kernel/timer.h", "kernel/timer.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "timer.h: timer_init() timer_ticks() sleep_ms(unsigned int ms). "
                    "timer.c: PIT diviseur 11931 outb(0x43,0x36) outb(0x40,lo) outb(0x40,hi). "
                    "volatile unsigned int g_ticks=0. IRQ0 handler ticks++ EOI. "
                    "sleep_ms: boucle while(g_ticks < start + ms/10). kernel.c: timer_init()."
                ),
                "impact_attendu": "Horloge système",
                "complexite":     "MOYENNE",
            },
            {
                "nom":                  "Terminal 20 commandes + historique",
                "priorite":             "HAUTE",
                "categorie":            "app",
                "fichiers_a_modifier":  ["apps/terminal.h", "apps/terminal.c"],
                "fichiers_a_creer":     [],
                "fichiers_a_supprimer": [],
                "description": (
                    "20 cmds: help ver mem uptime cls echo reboot halt color calc about "
                    "credits ps sysinfo license snake pong time date clear. "
                    "Historique 20 entrées flèche haut/bas. ZERO stdlib. "
                    "Signatures: tm_init() tm_draw() tm_key(char k)."
                ),
                "impact_attendu": "Terminal complet type cmd.exe",
                "complexite":     "MOYENNE",
            },
            {
                "nom":                  "Allocateur mémoire bitmap 4KB",
                "priorite":             "HAUTE",
                "categorie":            "kernel",
                "fichiers_a_modifier":  ["kernel/kernel.c", "Makefile"],
                "fichiers_a_creer":     ["kernel/memory.h", "kernel/memory.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "memory.h: mem_init(unsigned int start, unsigned int end) "
                    "mem_alloc()→unsigned int mem_free(unsigned int addr) "
                    "mem_used() mem_total(). "
                    "bitmap[1024] unsigned int 32MB/4KB. ZERO NULL→0. "
                    "kernel.c: mem_init(0x200000, 0x2000000)."
                ),
                "impact_attendu": "Allocation mémoire",
                "complexite":     "HAUTE",
            },
            {
                "nom":                  "VGA mode 13h 320x200 + desktop",
                "priorite":             "NORMALE",
                "categorie":            "driver",
                "fichiers_a_modifier":  ["drivers/screen.h", "drivers/screen.c", "kernel/kernel.c", "Makefile"],
                "fichiers_a_creer":     ["drivers/vga.h", "drivers/vga.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "vga.h: v_init() v_pixel(int x,int y,unsigned char c) "
                    "v_rect(int x,int y,int w,int h,unsigned char c) v_fill(unsigned char c). "
                    "vga.c: mode 13h (unsigned char*)0xA0000 desktop bleu(1) taskbar grise(7) bas 10px. "
                    "outb/inb depuis io.h — NE PAS redéfinir outb/inb dans vga.c. "
                    "ZERO stdlib. kernel.c: v_init()."
                ),
                "impact_attendu": "Interface graphique QEMU",
                "complexite":     "HAUTE",
            },
        ],
    }

def _parse_json(resp):
    if not resp:
        return None
    clean = resp.strip()
    if clean.startswith("```"):
        ls = clean.split("\n")
        if ls[-1].strip() == "```":
            ls = ls[1:-1]
        else:
            ls = ls[1:]
        clean = "\n".join(ls).strip()
    i = clean.find("{")
    j = clean.rfind("}") + 1
    if i < 0 or j <= i:
        return None
    candidate = clean[i:j]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass
    fixed = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', candidate)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError as ex:
        if DEBUG:
            log(f"JSON parse fail: {ex}", "WARN")
        return None

def phase_analyse(context, stats):
    log("=== PHASE 1: ANALYSE ===")
    disc_now("🔍 Analyse", f"`{stats['files']}` fichiers | `{stats['lines']}` lignes", 0x5865F2)

    prompt = (
        f"Expert OS bare metal x86. Réponds UNIQUEMENT avec du JSON valide.\n"
        f"{RULES}\n{OS_MISSION}\n\n"
        f"{context}\n\n"
        f"STATS: {stats['files']} fichiers, {stats['lines']} lignes\n\n"
        "JSON STRICT (commence par { finit par }, rien d'autre):\n"
        '{"score_actuel":30,"niveau_os":"Prototype","fonctionnalites_presentes":["Boot x86"],'
        '"fonctionnalites_manquantes_critiques":["IDT"],'
        '"plan_ameliorations":[{"nom":"IDT","priorite":"CRITIQUE","categorie":"kernel",'
        '"fichiers_a_modifier":["kernel/kernel.c"],"fichiers_a_creer":["kernel/idt.h"],'
        '"fichiers_a_supprimer":[],"description":"specs complètes","impact_attendu":"stable","complexite":"HAUTE"}],'
        '"prochaine_milestone":"Kernel stable"}'
    )

    resp = ai_call(prompt, max_tokens=3000, timeout=60, tag="analyse")
    if not resp:
        log("Analyse KO → plan défaut", "WARN")
        return default_plan()

    log(f"Analyse: {len(resp):,} chars")
    result = _parse_json(resp)
    if result and "plan_ameliorations" in result:
        nb = len(result.get("plan_ameliorations", []))
        log(f"Analyse OK: score={result.get('score_actuel','?')} {nb} tâches", "OK")
        return result

    log("JSON invalide ou incomplet → plan défaut", "WARN")
    return default_plan()

def task_ctx(task, sources):
    needed = set(
        task.get("fichiers_a_modifier", []) +
        task.get("fichiers_a_creer", [])
    )
    for f in list(needed):
        if f.endswith(".c"):
            needed.add(f.replace(".c", ".h"))
        elif f.endswith(".h"):
            needed.add(f.replace(".h", ".c"))
    for e in ["kernel/kernel.c", "kernel/kernel_entry.asm", "Makefile", "linker.ld",
              "drivers/screen.h", "kernel/io.h"]:
        needed.add(e)
    ctx  = ""
    used = 0
    for f in sorted(needed):
        c = sources.get(f, "")
        b = f"--- {f} ---\n{c if c else '[À CRÉER]'}\n\n"
        if used + len(b) > 22000:
            ctx += f"[{f} tronqué]\n"
            continue
        ctx  += b
        used += len(b)
    return ctx

def impl_prompt(task, ctx):
    return (
        f"{RULES}\n\n"
        f"TÂCHE: {task.get('nom', '?')}\n"
        f"CAT: {task.get('categorie', '?')} | CX: {task.get('complexite', '?')}\n"
        f"MODIFIER: {task.get('fichiers_a_modifier', [])}\n"
        f"CRÉER: {task.get('fichiers_a_creer', [])}\n"
        f"SUPPRIMER: {task.get('fichiers_a_supprimer', [])}\n"
        f"SPECS: {task.get('description', '')}\n\n"
        f"CODE EXISTANT:\n{ctx}\n\n"
        "RÈGLES CRITIQUES SUPPLÉMENTAIRES:\n"
        "- isr.asm/idt_handlers.asm: PAS de %macro ni %rep — écrire chaque isr0: isr1: ... isr47: EXPLICITEMENT\n"
        "- outb/inb: UNIQUEMENT dans kernel/io.h en static inline — jamais redéfinis ailleurs\n"
        "- kernel_entry.asm: global _stack_top doit être la PREMIÈRE ligne de code\n"
        "- Chaque fichier .c doit #include son propre .h\n"
        "- ZERO '...' ZERO commentaire ZERO stdlib\n\n"
        "FORMAT STRICT OBLIGATOIRE:\n"
        "=== FILE: chemin/fichier.ext ===\n"
        "[code complet]\n"
        "=== END FILE ===\n\n"
        "GÉNÈRE MAINTENANT:"
    )

def auto_fix(build_log, errs, gen_files, bak, model, max_att=4):
    log(f"Auto-fix: {len(errs)} erreur(s)", "BUILD")
    cur_log  = build_log
    cur_errs = errs

    for att in range(1, max_att + 1):
        log(f"Fix {att}/{max_att}", "BUILD")
        disc_log(f"🔧 Fix {att}/{max_att}", f"`{len(cur_errs)}` erreur(s)", 0x00AAFF)

        curr = {}
        for p in gen_files:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp):
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    curr[p] = f.read()[:10000]

        ctx     = "".join(f"--- {p} ---\n{c}\n\n" for p, c in curr.items())
        err_str = "\n".join(cur_errs[:15])

        prompt = (
            f"{RULES}\n\n"
            "ERREURS DE COMPILATION:\n"
            f"```\n{err_str}\n```\n\n"
            f"LOG COMPLET (fin):\n```\n{cur_log[-2500:]}\n```\n\n"
            f"FICHIERS ACTUELS:\n{ctx}\n\n"
            "CORRECTIONS REQUISES:\n"
            "- Si erreur 'multiple definition of outb/inb': retirer outb/inb du fichier fautif, #include \"kernel/io.h\"\n"
            "- Si erreur 'identifier expected after global got isr%i': réécrire TOUS les stubs explicitement sans macro\n"
            "- Si erreur 'undeclared': ajouter le #include manquant ou créer la déclaration\n"
            "- Si 'undefined reference': vérifier que le .c est dans Makefile OBJS\n\n"
            "ZERO commentaire. ZERO stdlib. FORMAT STRICT:\n"
            "=== FILE: fichier ===\n[code]\n=== END FILE ==="
        )

        resp = ai_call(prompt, max_tokens=28672, timeout=120, tag=f"fix/{att}")
        if not resp:
            wait = min(8 * (2 ** (att - 1)), 40)
            time.sleep(wait)
            continue

        files, _ = parse_ai_files(resp)
        if not files:
            log("Fix: rien parsé", "WARN")
            wait = min(8 * (2 ** (att - 1)), 40)
            time.sleep(wait)
            continue

        write_files(files)
        ok, cur_log, cur_errs = make_build()

        if ok:
            model_u = alive()[0]["model"] if alive() else model
            git_push("fix: corrections build", list(files.keys()), f"auto-fix {len(errs)}→0", model_u)
            disc_now("🔧 Fix ✅", f"{len(errs)} err→0 en {att} att", 0x00AAFF)
            return True, {"attempts": att}

        log(f"Fix {att}: encore {len(cur_errs)} err", "WARN")
        wait = min(5 * (2 ** (att - 1)), 30)
        time.sleep(wait)

    restore(bak)
    return False, {"attempts": max_att}

def implement(task, sources, i, total):
    nom   = task.get("nom", f"Tâche {i}")
    cat   = task.get("categorie", "?")
    prio  = task.get("priorite", "?")
    cx    = task.get("complexite", "MOYENNE")
    desc  = task.get("description", "")
    f_mod = task.get("fichiers_a_modifier", [])
    f_new = task.get("fichiers_a_creer", [])
    model = alive()[0]["model"] if alive() else "?"

    log(f"\n{'='*54}\n[{i}/{total}] [{prio}] {nom}\n{'='*54}")
    disc_now(
        f"🚀 [{i}/{total}] {nom[:55]}",
        f"```\n{pbar(int((i - 1) / total * 100))}\n```\n{desc[:250]}",
        0xFFA500,
        [
            {"name": "Priorité",  "value": prio,                                                          "inline": True},
            {"name": "Catégorie", "value": cat,                                                           "inline": True},
            {"name": "Complexité","value": cx,                                                            "inline": True},
            {"name": "Cibles",    "value": ", ".join(f"`{f}`" for f in (f_mod + f_new)[:6])[:400],       "inline": False},
            {"name": "Providers", "value": prov_summary()[:500],                                          "inline": False},
        ]
    )

    t0      = time.time()
    ctx     = task_ctx(task, sources)
    max_tok = {"HAUTE": 32768, "MOYENNE": 24576, "BASSE": 16384}.get(cx, 24576)
    prompt  = impl_prompt(task, ctx)

    resp    = ai_call(prompt, max_tokens=max_tok, timeout=170, tag=f"impl/{nom[:16]}")
    elapsed = round(time.time() - t0, 1)

    if not resp:
        disc_now(f"❌ [{i}/{total}] {nom[:50]}", f"IA indisponible après {elapsed}s", 0xFF4444)
        return False, [], [], {
            "nom": nom, "elapsed": elapsed, "result": "ai_fail", "errors": [],
        }

    files, to_del = parse_ai_files(resp)

    if not files and not to_del:
        disc_now(f"❌ [{i}/{total}] {nom[:50]}", "Rien parsé dans la réponse.", 0xFF6600)
        return False, [], [], {
            "nom": nom, "elapsed": elapsed, "result": "parse_empty", "errors": [],
        }

    disc_log(
        f"📁 {len(files)} fichier(s)",
        "\n".join(f"`{f}` {len(c):,}c" for f, c in list(files.items())[:8]),
        0x00AAFF
    )

    bak_f   = backup(list(files.keys()))
    written = write_files(files)
    deleted = del_files(to_del)

    if not written and not deleted:
        return False, [], [], {
            "nom": nom, "elapsed": elapsed, "result": "no_files", "errors": [],
        }

    ok, build_log, errs = make_build()

    if ok:
        pushed, sha, commit_short = git_push(nom, written + deleted, desc, model)
        total_elapsed = round(time.time() - t0, 1)
        if pushed and sha:
            m = {
                "nom":       nom,
                "elapsed":   total_elapsed,
                "result":    "success",
                "sha":       sha,
                "files":     written + deleted,
                "model":     model,
                "fix_count": 0,
            }
            fs_str = "\n".join(f"`{f}`" for f in (written + deleted)[:6]) or "aucun"
            disc_now(
                f"✅ [{i}/{total}] {nom[:50]}",
                f"```\n{pbar(int(i / total * 100))}\n```\nCommit: `{sha}`",
                0x00FF88,
                [
                    {"name": "⏱️",      "value": f"{total_elapsed:.0f}s",         "inline": True},
                    {"name": "📁",      "value": str(len(written + deleted)),      "inline": True},
                    {"name": "🤖",      "value": model[:30],                       "inline": True},
                    {"name": "Fichiers","value": fs_str,                           "inline": False},
                ]
            )
            return True, written, deleted, m
        elif pushed and sha is None:
            m = {
                "nom":       nom,
                "elapsed":   total_elapsed,
                "result":    "success_no_change",
                "sha":       git_sha(),
                "files":     [],
                "model":     model,
                "fix_count": 0,
            }
            return True, [], [], m
        else:
            restore(bak_f)
            return False, [], [], {
                "nom": nom, "elapsed": elapsed, "result": "push_fail", "errors": [],
            }

    fixed, fix_m = auto_fix(build_log, errs, list(files.keys()), bak_f, model)

    if fixed:
        total_elapsed = round(time.time() - t0, 1)
        fc            = fix_m.get("attempts", 0)
        m             = {
            "nom":       nom,
            "elapsed":   total_elapsed,
            "result":    "success_after_fix",
            "sha":       git_sha(),
            "files":     written + deleted,
            "model":     model,
            "fix_count": fc,
        }
        disc_now(
            f"✅ [{i}/{total}] {nom[:50]} (fix×{fc})",
            f"```\n{pbar(int(i / total * 100))}\n```",
            0x00BB66,
            [
                {"name": "⏱️", "value": f"{total_elapsed:.0f}s", "inline": True},
                {"name": "Fix", "value": str(fc),                "inline": True},
            ]
        )
        return True, written, deleted, m

    restore(bak_f)
    for p in written:
        if p not in bak_f:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp):
                os.remove(fp)
    SOURCE_CACHE["hash"] = None

    es = "\n".join(f"`{e[:80]}`" for e in errs[:5])
    disc_now(
        f"❌ [{i}/{total}] {nom[:50]}",
        f"Build fail après {fix_m.get('attempts', 0)} tentatives de fix.",
        0xFF4444,
        [
            {"name": "Erreurs", "value": es[:900] or "?",              "inline": False},
            {"name": "⏱️",      "value": f"{round(time.time()-t0,1):.0f}s", "inline": True},
        ]
    )
    return False, [], [], {
        "nom":    nom,
        "elapsed": round(time.time() - t0, 1),
        "result":  "build_fail",
        "errors":  errs[:5],
    }

BOT_LOGINS = {"MaxOS-AI-Bot", "github-actions[bot]", "dependabot[bot]", "maxos-ai[bot]"}

def _bot_already_commented(n):
    comments = gh_issue_comments(n)
    return any(
        c.get("user", {}).get("login", "") in BOT_LOGINS
        for c in (comments or [])
    )

def handle_issues():
    issues = gh_open_issues()
    if not issues:
        log("Issues: aucune")
        return
    log(f"Issues: {len(issues)}")
    ms_cache = {}

    for issue in issues[:12]:
        n      = issue.get("number")
        title  = issue.get("title", "")
        author = issue.get("user", {}).get("login", "")
        body_t = (issue.get("body", "") or "")[:800]
        labels = [l.get("name", "") for l in issue.get("labels", [])]

        if author in BOT_LOGINS:
            continue
        if _bot_already_commented(n):
            log(f"Issue #{n}: déjà traitée, skip")
            continue

        log(f"Issue #{n}: {title[:60]}")

        prompt = (
            f"Bot GitHub pour MaxOS OS bare metal x86.\n"
            f"ISSUE #{n}: {title}\nAuteur: {author}\n"
            f"Labels existants: {', '.join(labels) or 'aucun'}\n"
            f"Corps:\n{body_t}\n\n"
            "Réponds UNIQUEMENT avec du JSON valide:\n"
            '{"type":"bug|enhancement|question|invalid|duplicate",'
            '"priority":"critical|high|medium|low",'
            '"component":"kernel|driver|app|build|doc|other",'
            '"labels_add":["bug"],'
            '"milestone":"Kernel stable IDT+Timer|null",'
            '"action":"respond|close|close_not_planned|label_only",'
            '"response":"réponse utile détaillée en français",'
            '"duplicate_of":null}'
        )

        a = _parse_json(ai_call(prompt, max_tokens=800, timeout=35, tag=f"issue/{n}"))
        if not a:
            continue

        action     = a.get("action", "label_only")
        labels_add = [l for l in a.get("labels_add", []) if l in STANDARD_LABELS]
        resp_t     = a.get("response", "")
        itype      = a.get("type", "?")
        component  = a.get("component", "other")
        ms_title   = a.get("milestone")
        dup_of     = a.get("duplicate_of")

        if component in STANDARD_LABELS and component not in labels_add:
            labels_add.append(component)
        if labels_add:
            gh_add_labels(n, labels_add)

        if ms_title and ms_title != "null":
            if ms_title not in ms_cache:
                ms_cache[ms_title] = gh_ensure_milestone(ms_title)
            ms_num = ms_cache.get(ms_title)
            if ms_num:
                gh_assign_ms(n, ms_num)

        model_u = alive()[0]["model"] if alive() else "?"
        if resp_t and action in ("respond", "close", "close_not_planned"):
            dup_note = f"\n\n> Doublon possible de #{dup_of}" if dup_of else ""
            gh_post_comment(
                n,
                f"## 🤖 MaxOS AI — Réponse automatique\n\n"
                f"{resp_t}{dup_note}\n\n"
                f"---\n*Type: `{itype}` | Composant: `{component}` | {model_u} | MaxOS AI v{VERSION}*"
            )

        if action == "close":
            gh_close_issue(n, "completed")
            log(f"Issue #{n}: fermée (completed)")
        elif action == "close_not_planned":
            gh_close_issue(n, "not_planned")
            log(f"Issue #{n}: fermée (not_planned)")

        disc_log(f"🎫 Issue #{n} — {itype}", f"`{action}` | `{component}`", 0x5865F2)
        time.sleep(1)

def handle_stale(days_stale=21, days_close=7):
    issues    = gh_open_issues()
    now       = time.time()
    stale_s   = days_stale * 86400
    close_s   = (days_stale + days_close) * 86400
    sc = cc   = 0

    for issue in issues:
        n      = issue.get("number")
        upd    = issue.get("updated_at", "")
        labels = [l.get("name", "") for l in issue.get("labels", [])]
        author = issue.get("user", {}).get("login", "")
        if author in BOT_LOGINS:
            continue
        is_st = "stale" in labels
        try:
            upd_ts = datetime.strptime(upd, "%Y-%m-%dT%H:%M:%SZ").timestamp()
        except Exception:
            continue
        age = now - upd_ts

        if age >= close_s and is_st:
            gh_post_comment(
                n,
                f"🤖 **MaxOS AI**: Issue fermée automatiquement après **{int(age/86400)} jours** d'inactivité."
            )
            gh_close_issue(n, "not_planned")
            cc += 1
        elif age >= stale_s and not is_st:
            gh_add_labels(n, ["stale"])
            gh_post_comment(
                n,
                f"⏰ **MaxOS AI**: Cette issue est inactive depuis **{int(age/86400)} jours**.\n"
                f"Elle sera fermée dans **{days_close} jours** si aucune activité.\n\n"
                f"Pour la garder ouverte, laissez un commentaire."
            )
            sc += 1

    if sc + cc > 0:
        log(f"Stale: {sc} marquées, {cc} fermées")
        disc_log("⏰ Stale", f"{sc} marquées | {cc} fermées", 0xAAAAAA)

def handle_prs():
    prs = gh_open_prs()
    if not prs:
        log("PRs: aucune")
        return
    log(f"PRs: {len(prs)}")

    for pr in prs[:6]:
        n      = pr.get("number")
        title  = pr.get("title", "")
        author = pr.get("user", {}).get("login", "")

        if author in BOT_LOGINS:
            continue
        revs = gh_pr_reviews(n)
        if any(r.get("user", {}).get("login", "") in BOT_LOGINS for r in (revs or [])):
            log(f"PR #{n}: déjà reviewée, skip")
            continue

        log(f"PR #{n}: {title[:60]}")
        files_d = gh_pr_files(n)
        commits = gh_pr_commits(n)

        file_list = "\n".join(
            f"- {f.get('filename','?')} (+{f.get('additions',0)} -{f.get('deletions',0)})"
            for f in files_d[:20]
        )
        patches = ""
        for f in [f for f in files_d if f.get("filename", "").endswith((".c", ".h", ".asm"))][:5]:
            p = f.get("patch", "")[:1500]
            if p:
                patches += f"\n--- {f.get('filename','')} ---\n{p}\n"

        commit_msgs = "\n".join(
            f"- {c.get('commit',{}).get('message','').split(chr(10))[0][:80]}"
            for c in (commits or [])[:8]
        )

        prompt = (
            f"Expert OS bare metal x86, code review.\n{RULES}\n\n"
            f"PR #{n}: {title}\nAuteur: {author}\n"
            f"Fichiers modifiés:\n{file_list}\n"
            f"Commits:\n{commit_msgs}\n"
            f"Extraits de diff:\n{patches}\n\n"
            "Réponds UNIQUEMENT avec du JSON valide:\n"
            '{"decision":"APPROVE|REQUEST_CHANGES|COMMENT",'
            '"summary":"résumé 2-3 phrases",'
            '"problems":["prob1"],'
            '"positives":["bon1"],'
            '"bare_metal_violations":["v1"],'
            '"inline_comments":[{"path":"kernel/idt.c","line":10,"body":"commentaire"}],'
            '"merge_safe":true,'
            '"security_issues":[]}'
        )

        a = _parse_json(ai_call(prompt, max_tokens=2500, timeout=60, tag=f"pr/{n}"))
        if not a:
            a = {}

        decision   = a.get("decision", "COMMENT")
        merge_safe = a.get("merge_safe", False)
        summary    = a.get("summary", "Analyse indisponible.")
        problems   = a.get("problems", [])
        positives  = a.get("positives", [])
        viols      = a.get("bare_metal_violations", [])
        inlines    = a.get("inline_comments", [])
        sec_issues = a.get("security_issues", [])

        icon = {"APPROVE": "✅", "REQUEST_CHANGES": "🔴", "COMMENT": "💬"}.get(decision, "💬")
        safe = "🟢 Safe à merger" if merge_safe else "🔴 Ne pas merger"

        body = f"## {icon} Code Review MaxOS AI — PR #{n}\n\n> **{decision}** | {safe}\n\n{summary}\n\n"
        if problems:
            body += "### ❌ Problèmes\n" + "\n".join(f"- {p}" for p in problems) + "\n\n"
        if positives:
            body += "### ✅ Points positifs\n" + "\n".join(f"- {p}" for p in positives) + "\n\n"
        if viols:
            body += "### ⚠️ Violations bare metal\n" + "\n".join(f"- `{v}`" for v in viols) + "\n\n"
        if sec_issues:
            body += "### 🔒 Problèmes sécurité\n" + "\n".join(f"- {s}" for s in sec_issues) + "\n\n"

        model_u = alive()[0]["model"] if alive() else "?"
        body   += f"\n---\n*MaxOS AI v{VERSION} | {model_u}*"

        if decision == "APPROVE" and merge_safe:
            gh_approve_pr(n, body)
            gh_add_labels(n, ["ai-approved", "ai-reviewed"])
        elif decision == "REQUEST_CHANGES":
            gh_req_changes(n, body, inlines if inlines else None)
            gh_add_labels(n, ["ai-rejected", "ai-reviewed", "needs-fix"])
        else:
            gh_post_review(n, body, "COMMENT", inlines if inlines else None)
            gh_add_labels(n, ["ai-reviewed"])

        cat_labels = set()
        for f in files_d[:10]:
            fn = f.get("filename", "")
            if "kernel/" in fn:
                cat_labels.add("kernel")
            if "drivers/" in fn:
                cat_labels.add("driver")
            if "apps/" in fn:
                cat_labels.add("app")
        if cat_labels:
            gh_add_labels(n, list(cat_labels))

        color = 0x00AAFF if decision == "APPROVE" else 0xFF4444 if decision == "REQUEST_CHANGES" else 0xFFA500
        disc_log(f"📋 PR #{n} — {decision}", f"**{title[:40]}** | {safe}", color)
        log(f"PR #{n} → {decision}")
        time.sleep(1)

def create_release(tasks_done, tasks_failed, analyse, stats):
    releases = gh_list_releases(5)
    last_tag = "v0.0.0"
    for r in releases:
        tag = r.get("tag_name", "")
        if re.match(r"v\d+\.\d+\.\d+", tag):
            last_tag = tag
            break
    try:
        pts           = last_tag.lstrip("v").split(".")
        major, minor, patch = int(pts[0]), int(pts[1]), int(pts[2])
    except Exception:
        major = minor = patch = 0

    score = analyse.get("score_actuel", 30)
    if score >= 70:
        minor += 1
        patch  = 0
    else:
        patch += 1
    new_tag = f"v{major}.{minor}.{patch}"

    niveau   = analyse.get("niveau_os", "?")
    ms       = analyse.get("prochaine_milestone", "?")
    features = analyse.get("fonctionnalites_presentes", [])
    compare  = gh_compare(last_tag, "HEAD")
    commits  = compare.get("commits", [])
    chg_lines = [
        f"- `{c.get('sha','')[:7]}` {c.get('commit',{}).get('message','').split(chr(10))[0][:80]}"
        for c in commits[:20]
        if c.get("commit", {}).get("message", "")
    ]
    changelog = "\n".join(chg_lines) or "- Maintenance"

    changes = "".join(
        f"- ✅ {t.get('nom','?')[:55]} [`{t.get('sha','?')}`] "
        f"*{t.get('model','?')[:18]}*"
        f"{' (fix×'+str(t['fix_count'])+')' if t.get('fix_count',0)>0 else ''}\n"
        for t in tasks_done
    )
    failed_s = (
        "\n## ⏭️ Reporté\n\n" +
        "\n".join(f"- ❌ {n}" for n in tasks_failed) + "\n"
        if tasks_failed else ""
    )
    feat_txt = "\n".join(f"- ✅ {f}" for f in features[:8]) or "- (aucune)"

    tk      = sum(p["tokens"] for p in PROVIDERS)
    calls   = sum(p["calls"]  for p in PROVIDERS)
    types   = ", ".join(sorted({p["type"] for p in PROVIDERS if p["calls"] > 0})) or "?"
    elapsed = int(time.time() - START_TIME)
    now     = datetime.utcnow()

    repo_stats = gh_repo_stats()

    body = (
        f"# MaxOS {new_tag}\n\n> 🤖 MaxOS AI v{VERSION} — Génération automatique\n\n---\n\n"
        f"## 📊 État du projet\n"
        f"| Métrique | Valeur |\n|---|---|\n"
        f"| Score qualité | **{score}/100** |\n"
        f"| Niveau | {niveau} |\n"
        f"| Fichiers sources | {stats.get('files',0)} |\n"
        f"| Lignes de code | {stats.get('lines',0):,} |\n"
        f"| Prochaine milestone | {ms} |\n"
        f"| ⭐ Stars | {repo_stats.get('stars',0)} |\n"
        f"| 🍴 Forks | {repo_stats.get('forks',0)} |\n\n"
        f"## ✅ Changements cette version\n\n{changes}{failed_s}\n"
        f"## 📝 Changelog {last_tag}→{new_tag}\n\n{changelog}\n\n"
        f"## 🧩 Fonctionnalités\n\n{feat_txt}\n\n"
        f"## 🚀 Tester\n\n"
        f"```bash\nqemu-system-i386 -drive format=raw,file=os.img,if=floppy -boot a -vga std -k fr -m 32\n```\n\n"
        f"## 🤖 Statistiques IA\n"
        f"| IA | Appels | ~Tokens | Durée |\n|---|---|---|---|\n"
        f"| {types} | {calls} | {tk:,} | {elapsed}s |\n\n"
        f"*MaxOS AI v{VERSION} | {now.strftime('%Y-%m-%d %H:%M')} UTC*\n"
    )

    url = gh_create_release(
        new_tag,
        f"MaxOS {new_tag} | {niveau} | {now.strftime('%Y-%m-%d')}",
        body,
        pre=(score < 50)
    )
    if url:
        disc_now(
            "🚀 Release créée",
            f"**{new_tag}** | Score: {score}/100",
            0x00FF88,
            [
                {"name": "Version", "value": new_tag,           "inline": True},
                {"name": "Score",   "value": f"{score}/100",    "inline": True},
                {"name": "Lien",    "value": f"[Release]({url})","inline": False},
            ]
        )
        log(f"Release {new_tag} → {url}", "OK")
    return url

def final_report(success, total, tasks_done, tasks_failed, analyse, stats):
    score   = analyse.get("score_actuel", 30)
    niveau  = analyse.get("niveau_os", "?")
    pct     = int(success / total * 100) if total > 0 else 0
    color   = 0x00FF88 if pct >= 80 else 0xFFA500 if pct >= 50 else 0xFF4444
    elapsed = int(time.time() - START_TIME)
    tk      = sum(p["tokens"] for p in PROVIDERS)
    calls   = sum(p["calls"]  for p in PROVIDERS)

    sources = read_all()
    qual    = analyze_quality(sources)

    done_s = "\n".join(
        f"✅ {t.get('nom','?')[:40]} ({t.get('elapsed',0):.0f}s)"
        for t in tasks_done
    ) or "Aucune"
    fail_s = "\n".join(f"❌ {n[:40]}" for n in tasks_failed) or "Aucune"

    prov_detail = []
    for p in sorted(PROVIDERS, key=lambda x: -x["calls"]):
        if p["calls"] == 0:
            continue
        avg_r = avg_rt(p)
        status = "💀" if p["dead"] else "🟢"
        prov_detail.append(
            f"{status} `{p['id']}` {p['calls']}c ~{p['tokens']:,}tk avg{avg_r:.0f}s"
        )

    disc_now(
        f"🏁 Cycle terminé — {success}/{total}",
        f"```\n{pbar(pct)}\n```",
        color,
        [
            {"name": "✅ Succès",   "value": str(success),          "inline": True},
            {"name": "❌ Échecs",   "value": str(total - success),  "inline": True},
            {"name": "📈 Taux",     "value": f"{pct}%",             "inline": True},
            {"name": "⏱️ Durée",    "value": f"{elapsed}s",         "inline": True},
            {"name": "🔑 Appels",   "value": str(calls),            "inline": True},
            {"name": "💬 ~Tokens",  "value": f"{tk:,}",             "inline": True},
            {"name": "📊 Qualité",  "value": f"{qual['score']}/100","inline": True},
            {"name": "📁 Fichiers", "value": str(stats.get("files",0)),"inline": True},
            {"name": "📝 Lignes",   "value": str(stats.get("lines",0)),"inline": True},
            {"name": "🏆 Score OS", "value": f"{score}/100 — {niveau}", "inline": False},
            {"name": "✅ Réussies", "value": done_s[:800],          "inline": False},
            {"name": "❌ Échouées", "value": fail_s[:400],          "inline": False},
            {"name": "🔑 Providers","value": prov_summary()[:600],  "inline": False},
            {"name": "📡 Détail",   "value": "\n".join(prov_detail[:8])[:600] or "?", "inline": False},
        ]
    )

    if qual["violations"]:
        disc_now(
            "⚠️ Violations bare metal",
            "```\n" + "\n".join(f"• {v}" for v in qual["violations"][:15]) + "\n```",
            0xFF6600
        )

def main():
    print("=" * 62)
    print(f"  MaxOS AI Developer v{VERSION}")
    print(f"  Multi-provider | GitHub maximal | Bare metal x86")
    print("=" * 62)

    if not PROVIDERS:
        print("FATAL: Aucun provider configuré.")
        print("  Secrets: GEMINI_API_KEY, OPENROUTER_KEY, GROQ_KEY, MISTRAL_KEY")
        sys.exit(1)

    by_type = {}
    for p in PROVIDERS:
        by_type.setdefault(p["type"], []).append(p)
    for t, ps in sorted(by_type.items()):
        ku = len(set(p["key"][:8] for p in ps))
        mu = len(set(p["model"] for p in ps))
        print(f"  {t:12s}: {ku} clé(s) × {mu} modèle(s) = {len(ps)} providers")
    print(f"  {'TOTAL':12s}: {len(PROVIDERS)} providers")
    print("=" * 62 + "\n")

    disc_now(
        f"🤖 MaxOS AI v{VERSION} démarré",
        f"`{len(PROVIDERS)}` providers configurés",
        0x5865F2,
        [
            {"name": "Providers", "value": prov_summary()[:800], "inline": False},
            {"name": "Repo",      "value": f"{REPO_OWNER}/{REPO_NAME}", "inline": True},
            {"name": "Debug",     "value": "ON" if DEBUG else "OFF",    "inline": True},
            {"name": "Runtime",   "value": f"{MAX_RUNTIME}s max",       "inline": True},
        ]
    )

    subprocess.run(["make", "clean"], cwd=REPO_PATH, capture_output=True, timeout=30)

    log("Setup: labels GitHub")
    gh_ensure_labels(STANDARD_LABELS)

    log("[Issues] Traitement...")
    handle_issues()
    if not watchdog():
        sys.exit(0)

    log("[Stale] Vérification issues inactives...")
    handle_stale(days_stale=21, days_close=7)

    log("[PRs] Traitement...")
    handle_prs()
    if not watchdog():
        sys.exit(0)

    sources = read_all(force=True)
    stats   = proj_stats(sources)
    qual    = analyze_quality(sources)
    log(f"Sources: {stats['files']} fichiers, {stats['lines']} lignes, {stats['chars']:,} chars")
    log(f"Qualité: {qual['score']}/100 | {len(qual['violations'])} violation(s)")

    disc_now(
        "📊 Sources analysées",
        f"`{stats['files']}` fichiers | `{stats['lines']:,}` lignes | `{stats['chars']:,}` chars",
        0x5865F2,
        [
            {"name": "Qualité", "value": f"{qual['score']}/100 ({len(qual['violations'])} violations)", "inline": True},
            {"name": ".c/.h",   "value": str(qual.get("c_files", 0)),  "inline": True},
            {"name": ".asm",    "value": str(qual.get("asm_files", 0)),"inline": True},
        ]
    )

    analyse   = phase_analyse(build_ctx(sources), stats)
    score     = analyse.get("score_actuel", 30)
    niveau    = analyse.get("niveau_os", "?")
    plan      = analyse.get("plan_ameliorations", [])
    milestone = analyse.get("prochaine_milestone", "?")
    features  = analyse.get("fonctionnalites_presentes", [])
    manques   = analyse.get("fonctionnalites_manquantes_critiques", [])

    order = {"CRITIQUE": 0, "HAUTE": 1, "NORMALE": 2, "BASSE": 3}
    plan  = sorted(plan, key=lambda t: order.get(t.get("priorite", "NORMALE"), 2))

    log(f"Score={score} | {niveau} | {len(plan)} tâche(s)", "OK")

    if milestone:
        ms_num = gh_ensure_milestone(milestone)
        if ms_num:
            log(f"Milestone '{milestone}' = #{ms_num}")

    disc_now(
        f"📊 Score {score}/100 — {niveau}",
        f"```\n{pbar(score)}\n```",
        0x00AAFF if score >= 60 else 0xFFA500 if score >= 30 else 0xFF4444,
        [
            {"name": "✅ Présentes",  "value": "\n".join(f"+ {f}" for f in features[:6]) or "?",  "inline": True},
            {"name": "❌ Manquantes", "value": "\n".join(f"- {f}" for f in manques[:6]) or "?",   "inline": True},
            {"name": "📋 Plan",
             "value": "\n".join(
                 f"[{i+1}] `{t.get('priorite','?')}` {t.get('nom','?')[:35]}"
                 for i, t in enumerate(plan[:7])
             ),
             "inline": False},
            {"name": "🎯 Milestone", "value": milestone[:80],      "inline": True},
            {"name": "🔑 Providers", "value": prov_summary()[:400],"inline": False},
        ]
    )

    total        = len(plan)
    success      = 0
    tasks_done   = []
    tasks_failed = []

    for i, task in enumerate(plan, 1):
        if not watchdog():
            break

        disc_log(
            f"💓 [{i}/{total}] {task.get('nom','?')[:45]}",
            f"Uptime: {uptime()} | {prov_summary()[:250]}",
            0x7289DA
        )

        sources_now = read_all()
        ok, written, deleted, metrics = implement(task, sources_now, i, total)
        TASK_METRICS.append(metrics)

        if ok:
            success      += 1
            tasks_done.append(metrics)
        else:
            tasks_failed.append(task.get("nom", "?"))

        if i < total:
            n_al  = len(alive())
            pause = 4 if n_al >= 4 else 8 if n_al >= 2 else 15
            log(f"Pause {pause}s ({n_al} provider(s) dispo)")
            _flush_disc(True)
            time.sleep(pause)

    if success > 0:
        log("\n[Release] Création...")
        sf = read_all(force=True)
        create_release(tasks_done, tasks_failed, analyse, proj_stats(sf))

    sf = read_all(force=True)
    final_report(success, total, tasks_done, tasks_failed, analyse, proj_stats(sf))
    _flush_disc(True)

    print(f"\n{'='*62}")
    print(f"[FIN] {success}/{total} | uptime: {uptime()} | GH RL: {GH_RATE['remaining']}")
    print(f"      {prov_summary().split(chr(10))[0]}")
    for t in tasks_done:
        fc = t.get("fix_count", 0)
        print(f"  ✅ {t.get('nom','?')[:55]} ({t.get('elapsed',0):.0f}s){' fix×'+str(fc) if fc else ''}")
    for n in tasks_failed:
        print(f"  ❌ {n[:55]}")
    print("=" * 62)

if __name__ == "__main__":
    main()
