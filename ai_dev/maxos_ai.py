#!/usr/bin/env python3
"""MaxOS AI Developer v16.0 — Ultra-robust, API-efficient, bare metal x86"""

import os, sys, json, time, subprocess, re, hashlib, traceback, random, socket, atexit
import urllib.request, urllib.error, urllib.parse
from datetime import datetime, timezone
from collections import defaultdict, deque

VERSION     = "16.0"
DEBUG       = os.environ.get("MAXOS_DEBUG", "0") == "1"
START_TIME  = time.time()
MAX_RUNTIME = 3300

REPO_OWNER = os.environ.get("REPO_OWNER", "MaxLananas")
REPO_NAME  = os.environ.get("REPO_NAME",  "MaxOS")
REPO_PATH  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GH_TOKEN   = os.environ.get("GH_PAT", "") or os.environ.get("GITHUB_TOKEN", "")
DISCORD_WH = os.environ.get("DISCORD_WEBHOOK", "")

# ─── PROVIDER MODELS ────────────────────────────────────────────────────────
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

OPENROUTER_MODELS = [
    "google/gemini-2.5-flash-preview-05-20",
    "qwen/qwen3-235b-a22b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "mistralai/devstral-small:free",
    "tngtech/deepseek-r1t-chimera:free",
    "deepseek/deepseek-chat-v3-0324:free",
]

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "qwen-qwen3-32b",
    "moonshotai/kimi-k2-instruct",
]

MISTRAL_MODELS = [
    "mistral-small-latest",
    "mistral-medium-latest",
    "open-mixtral-8x7b",
]

# ─── DEAD MODELS CACHE (permanent failures, never retry) ────────────────────
_DEAD_MODEL_IDS: set = set()  # provider IDs marked dead permanently
_KEY_ERRORS: dict = {}        # key_prefix -> error_count (propagate invalids)

# ─── GLOBAL STATE ────────────────────────────────────────────────────────────
GH_RATE      = {"remaining": 5000, "reset": 0}
SOURCE_CACHE = {"hash": None, "data": None}
TASK_METRICS = []
_DISC_BUF    = []
_DISC_LAST   = 0.0
_DISC_INTV   = 15
_CYCLE_STATS = defaultdict(int)
_RR          = 0

def ts():
    return datetime.now(timezone.utc).strftime("%H:%M:%S")

def uptime():
    s    = int(time.time() - START_TIME)
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def remaining_time():
    return max(0, MAX_RUNTIME - (time.time() - START_TIME))

def pbar(pct, w=20):
    pct = max(0, min(100, pct))
    f   = int(w * pct / 100)
    return "█" * f + "░" * (w - f) + f" {pct}%"

ICONS = {"INFO":"📋","WARN":"⚠️ ","ERROR":"❌","OK":"✅","BUILD":"🔨","GIT":"📦","TIME":"⏱️ ","AI":"🤖","STAT":"📊"}

def log(msg, level="INFO"):
    print(f"[{ts()}] {ICONS.get(level,'📋')} {msg}", flush=True)

def watchdog():
    elapsed = time.time() - START_TIME
    if elapsed >= MAX_RUNTIME:
        log(f"Watchdog: {int(elapsed)}s/{MAX_RUNTIME}s", "WARN")
        disc_now("⏰ Watchdog", f"Arrêt après **{uptime()}**", 0xFFA500)
        return False
    return True

# ─── PROVIDER LOADING ────────────────────────────────────────────────────────
def _find_keys(prefix):
    keys = []
    for suffix in [""] + [f"_{i}" for i in range(2, 12)]:
        v = os.environ.get(f"{prefix}{suffix}", "").strip()
        if len(v) >= 8:
            keys.append(v)
    return keys

def _make_provider(ptype, pid, key, model, url):
    return {
        "type": ptype, "id": pid, "key": key, "model": model, "url": url,
        "cooldown": 0.0, "errors": 0, "calls": 0, "tokens": 0,
        "dead": False, "last_ok": 0.0,
        "response_times": deque(maxlen=10),
        "consec_429": 0, "success_rate": 1.0,
        "key_prefix": key[:8],
    }

def load_providers():
    pools = []

    gem_keys = _find_keys("GEMINI_API_KEY")
    log(f"  [load] GEMINI     : {len(gem_keys)} key(s) × {len(GEMINI_MODELS)} = {len(gem_keys)*len(GEMINI_MODELS)}")
    gem = []
    for i, key in enumerate(gem_keys, 1):
        for m in GEMINI_MODELS:
            base = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
            slug = m.replace("gemini-","").replace("-","").replace(".","")[:14]
            gem.append(_make_provider("gemini", f"gm{i}_{slug}", key, m, f"{base}?key={key}"))
    if gem: pools.append(gem)

    or_keys = _find_keys("OPENROUTER_KEY")
    log(f"  [load] OPENROUTER : {len(or_keys)} key(s) × {len(OPENROUTER_MODELS)} = {len(or_keys)*len(OPENROUTER_MODELS)}")
    orl = []
    for i, key in enumerate(or_keys, 1):
        for m in OPENROUTER_MODELS:
            short = m.split("/")[-1].replace(":free","")[:16]
            orl.append(_make_provider("openrouter", f"or{i}_{short}", key, m,
                                      "https://openrouter.ai/api/v1/chat/completions"))
    if orl: pools.append(orl)

    groq_keys = _find_keys("GROQ_KEY")
    log(f"  [load] GROQ       : {len(groq_keys)} key(s) × {len(GROQ_MODELS)} = {len(groq_keys)*len(GROQ_MODELS)}")
    gro = []
    for i, key in enumerate(groq_keys, 1):
        for m in GROQ_MODELS:
            slug = m.replace("/","_").replace("-","_")[:16]
            gro.append(_make_provider("groq", f"gr{i}_{slug}", key, m,
                                      "https://api.groq.com/openai/v1/chat/completions"))
    if gro: pools.append(gro)

    mis_keys = _find_keys("MISTRAL_KEY")
    log(f"  [load] MISTRAL    : {len(mis_keys)} key(s) × {len(MISTRAL_MODELS)} = {len(mis_keys)*len(MISTRAL_MODELS)}")
    mis = []
    for i, key in enumerate(mis_keys, 1):
        for m in MISTRAL_MODELS:
            mis.append(_make_provider("mistral", f"ms{i}_{m[:16]}", key, m,
                                      "https://api.mistral.ai/v1/chat/completions"))
    if mis: pools.append(mis)

    # Interleave pools for diversity
    result  = []
    max_len = max((len(p) for p in pools), default=0)
    for i in range(max_len):
        for pool in pools:
            if i < len(pool):
                result.append(pool[i])
    return result

PROVIDERS = load_providers()

# ─── PROVIDER MANAGEMENT ─────────────────────────────────────────────────────
def alive():
    now = time.time()
    al  = [p for p in PROVIDERS
           if not p["dead"] and now >= p["cooldown"]]
    al.sort(key=lambda p: (p["consec_429"] * 5 + p["errors"] * 2, -p["success_rate"]))
    return al

def non_dead():
    return [p for p in PROVIDERS if not p["dead"]]

def avg_rt(p):
    rt = p.get("response_times", [])
    return sum(rt) / len(rt) if rt else 999.0

def prov_summary():
    now = time.time()
    by  = defaultdict(lambda: [0, 0, 0])
    for p in PROVIDERS:
        t = p["type"]
        if p["dead"]:          by[t][2] += 1
        elif now >= p["cooldown"]: by[t][0] += 1
        else:                  by[t][1] += 1
    parts = [f"**{t}**: 🟢{v[0]} 🟡{v[1]} 💀{v[2]}" for t, v in sorted(by.items())]
    return f"{len(alive())}/{len(non_dead())} dispo — " + " | ".join(parts)

def _propagate_key_dead(key_prefix):
    """Mark ALL providers sharing a dead key as dead."""
    count = 0
    for p in PROVIDERS:
        if p["key_prefix"] == key_prefix and not p["dead"]:
            p["dead"] = True
            count += 1
    if count:
        log(f"Key {key_prefix}*** → {count} provider(s) tués (clé invalide)", "ERROR")

def penalize(p, secs=None, dead=False):
    if dead:
        p["dead"] = True
        _DEAD_MODEL_IDS.add(p["id"])
        _CYCLE_STATS["providers_dead"] += 1
        log(f"Provider {p['id']} ({p['type']}/{p['model']}) → MORT", "ERROR")
        return
    p["errors"]      += 1
    p["consec_429"]  += 1
    p["success_rate"] = max(0.0, p["success_rate"] - 0.15)
    if secs is None:
        base   = 15 * (2 ** min(p["errors"] - 1, 4))
        secs   = min(base + random.uniform(0, 3), 180)
    p["cooldown"] = time.time() + secs
    log(f"Provider {p['id']} → cooldown {int(secs)}s (errs={p['errors']})", "WARN")

def reward(p, elapsed):
    p["errors"]      = max(0, p["errors"] - 1)
    p["consec_429"]  = 0
    p["last_ok"]     = time.time()
    p["success_rate"] = min(1.0, p["success_rate"] + 0.05)
    p["response_times"].append(elapsed)
    _CYCLE_STATS["total_calls"] += 1

def pick():
    global _RR
    al = alive()
    if al:
        # Weighted pick: best success_rate, lowest errors
        chosen = al[0]  # already sorted by quality
        if DEBUG:
            log(f"  pick → {chosen['id']} sr={chosen['success_rate']:.2f}", "INFO")
        return chosen
    nd = non_dead()
    if not nd:
        log("FATAL: tous les providers sont morts", "ERROR")
        disc_now("💀 Mort totale", "Aucun provider. Arrêt.", 0xFF0000)
        sys.exit(1)
    best = min(nd, key=lambda p: p["cooldown"])
    wait = min(max(best["cooldown"] - time.time() + 0.5, 0.5), 90)
    log(f"Tous en cooldown → attente {int(wait)}s → {best['id']}", "TIME")
    _CYCLE_STATS["total_waits"] += 1
    _CYCLE_STATS["total_wait_secs"] += int(wait)
    disc_log("⏳ Cooldown global", f"Attente **{int(wait)}s** → `{best['id']}`", 0xFF8800)
    time.sleep(wait)
    return best

# ─── API CALLS ───────────────────────────────────────────────────────────────
def _call_gemini(p, prompt, max_tok, timeout):
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tok,
            "temperature": 0.05,
            "candidateCount": 1,
        },
    }).encode("utf-8")
    req = urllib.request.Request(
        p["url"], data=payload,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode("utf-8"))
    cands = data.get("candidates", [])
    if not cands: return None
    c      = cands[0]
    finish = c.get("finishReason", "STOP")
    if finish in ("SAFETY", "RECITATION", "PROHIBITED_CONTENT"):
        return None
    parts = c.get("content", {}).get("parts", [])
    texts = [pt.get("text","") for pt in parts
             if isinstance(pt, dict) and not pt.get("thought") and pt.get("text")]
    result = "".join(texts).strip()
    return result if result else None

def _call_compat(p, prompt, max_tok, timeout):
    # Per-provider prompt limits
    limits = {"groq": 26000, "openrouter": 45000, "mistral": 50000}
    lim = limits.get(p["type"], 50000)
    if len(prompt) > lim:
        prompt = prompt[:lim] + "\n[TRONQUÉ]"
    if p["type"] == "groq":
        max_tok = min(max_tok, 8000)

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
        headers["X-Title"]      = f"MaxOS AI v{VERSION}"

    req = urllib.request.Request(p["url"], data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode("utf-8"))

    if "error" in data:
        raise RuntimeError(data["error"].get("message","unknown")[:250])

    choices = data.get("choices", [])
    if not choices: return None
    content = choices[0].get("message",{}).get("content","")
    return content.strip() if content else None

def ai_call(prompt, max_tokens=32768, timeout=160, tag="?"):
    if len(prompt) > 54000:
        prompt = prompt[:54000] + "\n[TRONQUÉ]"

    max_att    = min(len(PROVIDERS) * 2, 30)
    last_error = "aucune tentative"
    _CYCLE_STATS["ai_calls"] += 1

    for attempt in range(1, max_att + 1):
        if not watchdog(): return None
        p  = pick()
        t0 = time.time()
        log(f"[{tag}] {p['type']}/{p['id']} att={attempt} sr={p['success_rate']:.2f}", "AI")

        try:
            if p["type"] == "gemini":
                text = _call_gemini(p, prompt, max_tokens, timeout)
            else:
                text = _call_compat(p, prompt, max_tokens, timeout)

            elapsed = round(time.time() - t0, 1)

            if not text or not text.strip():
                log(f"[{tag}] Réponse vide ({p['id']}) {elapsed}s", "WARN")
                penalize(p, 12)
                continue

            p["calls"]  += 1
            p["tokens"] += len(text) // 4
            reward(p, elapsed)
            _CYCLE_STATS["total_tokens"] += len(text) // 4
            log(f"[{tag}] ✅ {len(text):,}c {elapsed}s ({p['type']}/{p['model'][:22]})", "OK")
            return text

        except urllib.error.HTTPError as e:
            elapsed = round(time.time() - t0, 1)
            body    = ""
            try:   body = e.read().decode("utf-8", errors="replace")[:600]
            except: pass
            last_error = f"HTTP {e.code}"
            log(f"[{tag}] HTTP {e.code} ({p['id']}) {elapsed}s", "WARN")

            if e.code == 429:
                _CYCLE_STATS["total_429"] += 1
                penalize(p)

            elif e.code == 401:
                # Key is definitely invalid — kill all providers with same key
                _propagate_key_dead(p["key_prefix"])

            elif e.code == 403:
                bl = body.lower()
                kill_words = ["denied","banned","suspended","not authorized",
                              "forbidden","deactivated","invalid api key","access denied"]
                if any(w in bl for w in kill_words):
                    _propagate_key_dead(p["key_prefix"])
                else:
                    penalize(p, 180)

            elif e.code == 404:
                # Model not found — kill just this provider, not the key
                penalize(p, dead=True)

            elif e.code == 400:
                # Likely bad model ID — kill this provider
                if "not a valid model" in body.lower() or "no endpoints found" in body.lower():
                    penalize(p, dead=True)
                else:
                    penalize(p, 40)

            elif e.code in (500, 502, 503, 504):
                penalize(p, 20)
                time.sleep(2)

            elif e.code == 408:
                penalize(p, 25)

            else:
                penalize(p, 15)
                time.sleep(1)

        except (TimeoutError, socket.timeout):
            elapsed = round(time.time() - t0, 1)
            log(f"[{tag}] TIMEOUT {timeout}s ({p['id']})", "WARN")
            last_error = f"timeout"
            penalize(p, 30)

        except urllib.error.URLError as e:
            log(f"[{tag}] URLError ({p['id']}): {e.reason}", "WARN")
            last_error = str(e.reason)[:100]
            penalize(p, 18)
            time.sleep(2)

        except RuntimeError as e:
            log(f"[{tag}] RuntimeError ({p['id']}): {e}", "WARN")
            last_error = str(e)[:100]
            penalize(p, 22)

        except json.JSONDecodeError as e:
            log(f"[{tag}] JSON error ({p['id']}): {e}", "WARN")
            penalize(p, 10)

        except Exception as e:
            log(f"[{tag}] Exception ({p['id']}): {type(e).__name__}: {e}", "ERROR")
            last_error = f"{type(e).__name__}: {str(e)[:80]}"
            if DEBUG: traceback.print_exc()
            penalize(p, 12)
            time.sleep(1)

    _CYCLE_STATS["ai_failures"] += 1
    log(f"[{tag}] ÉCHEC TOTAL {max_att} att. Dernière: {last_error}", "ERROR")
    return None

# ─── DISCORD ─────────────────────────────────────────────────────────────────
def _disc_raw(embeds):
    if not DISCORD_WH: return False
    payload = json.dumps({
        "username": f"MaxOS AI v{VERSION}",
        "embeds":   embeds[:10],
    }).encode()
    req = urllib.request.Request(
        DISCORD_WH, data=payload,
        headers={"Content-Type": "application/json", "User-Agent": f"MaxOS-Bot/{VERSION}"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status in (200, 204)
    except Exception as ex:
        if DEBUG: log(f"Discord err: {ex}", "WARN")
        return False

def _make_embed(title, desc, color, fields=None):
    al  = len(alive())
    nd  = len(non_dead())
    tk  = sum(p["tokens"] for p in PROVIDERS)
    ca  = sum(p["calls"]  for p in PROVIDERS)
    cur = alive()[0]["model"][:22] if alive() else "aucun"
    e   = {
        "title":       str(title)[:256],
        "description": str(desc)[:4096],
        "color":       color,
        "timestamp":   datetime.utcnow().isoformat() + "Z",
        "footer":      {"text": f"v{VERSION} | {cur} | {al}/{nd} | up {uptime()} | ~{tk:,}tk | {ca}c"},
    }
    if fields:
        e["fields"] = [
            {"name": str(f.get("name","?"))[:256],
             "value": str(f.get("value","?"))[:1024],
             "inline": bool(f.get("inline",False))}
            for f in fields[:25]
            if f.get("value") and str(f.get("value","")).strip()
        ]
    return e

def disc_log(title, desc="", color=0x5865F2):
    _DISC_BUF.append((title, desc, color))
    _flush_disc(False)

def _flush_disc(force=True):
    global _DISC_LAST
    now = time.time()
    if not force and now - _DISC_LAST < _DISC_INTV: return
    if not _DISC_BUF: return
    # Cap buffer size
    while len(_DISC_BUF) > 50:
        _DISC_BUF.pop(0)
    embeds = []
    while _DISC_BUF and len(embeds) < 10:
        t, d, c = _DISC_BUF.pop(0)
        embeds.append(_make_embed(t, d, c))
    if embeds:
        _disc_raw(embeds)
        _DISC_LAST = time.time()

def disc_now(title, desc="", color=0x5865F2, fields=None):
    _flush_disc(True)
    _disc_raw([_make_embed(title, desc, color, fields)])

atexit.register(_flush_disc, True)

# ─── GITHUB API ──────────────────────────────────────────────────────────────
def gh_api(method, endpoint, data=None, raw_url=None, retry=3, silent=False):
    if not GH_TOKEN: return None
    url     = raw_url or f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/{endpoint}"
    payload = json.dumps(data).encode() if data else None
    for att in range(1, retry + 1):
        req = urllib.request.Request(
            url, data=payload,
            headers={
                "Authorization": f"Bearer {GH_TOKEN}",
                "Accept":        "application/vnd.github+json",
                "Content-Type":  "application/json",
                "User-Agent":    f"MaxOS-AI/{VERSION}",
                "X-GitHub-Api-Version": "2022-11-28",
            }, method=method
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                rem = r.headers.get("X-RateLimit-Remaining")
                rst = r.headers.get("X-RateLimit-Reset")
                if rem: GH_RATE["remaining"] = int(rem)
                if rst: GH_RATE["reset"]     = int(rst)
                if GH_RATE["remaining"] < 80:
                    log(f"GH rate limit critique: {GH_RATE['remaining']} restants!", "WARN")
                raw = r.read().decode("utf-8", errors="replace")
                return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as e:
            body = ""
            try: body = e.read().decode("utf-8", errors="replace")[:400]
            except: pass
            if e.code == 403 and "rate limit" in body.lower():
                wait = max(GH_RATE["reset"] - time.time() + 5, 60)
                log(f"GH rate limit 403 → attente {int(wait)}s", "WARN")
                time.sleep(wait)
                continue
            if e.code in (500,502,503,504) and att < retry:
                time.sleep(5 * att)
                continue
            if not silent:
                log(f"GH {method} {endpoint[:60]} HTTP {e.code}: {body[:120]}", "WARN")
            return None
        except Exception as ex:
            if att < retry: time.sleep(3); continue
            if not silent: log(f"GH ex: {ex}", "ERROR")
            return None
    return None

def gh_open_prs():
    r = gh_api("GET", "pulls?state=open&per_page=20&sort=updated&direction=desc")
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
            {"path": c["path"], "line": c.get("line",1), "side":"RIGHT", "body": c["body"]}
            for c in comments if c.get("path") and c.get("body")
        ]
    return gh_api("POST", f"pulls/{n}/reviews", pay)

def gh_approve_pr(n, body):    return gh_post_review(n, body, "APPROVE")
def gh_req_changes(n, body, comments=None): return gh_post_review(n, body, "REQUEST_CHANGES", comments)

def gh_merge_pr(n, title):
    r = gh_api("PUT", f"pulls/{n}/merge", {
        "commit_title": f"merge: {title[:60]} [AI]",
        "merge_method": "squash",
    })
    return bool(r and r.get("merged"))

def gh_open_issues():
    r = gh_api("GET", "issues?state=open&per_page=30&sort=updated&direction=desc")
    if not isinstance(r, list): return []
    return [i for i in r if not i.get("pull_request")]

def gh_issue_comments(n):
    r = gh_api("GET", f"issues/{n}/comments?per_page=50")
    return r if isinstance(r, list) else []

def gh_close_issue(n, reason="completed"):
    gh_api("PATCH", f"issues/{n}", {"state":"closed","state_reason":reason})

def gh_add_labels(n, labels):
    if labels: gh_api("POST", f"issues/{n}/labels", {"labels": labels})

def gh_post_comment(n, body):
    gh_api("POST", f"issues/{n}/comments", {"body": body})

def gh_create_issue(title, body, labels=None):
    pay = {"title": title, "body": body}
    if labels: pay["labels"] = labels
    return gh_api("POST", "issues", pay)

def gh_list_labels():
    r = gh_api("GET", "labels?per_page=100")
    return {l["name"]: l for l in (r if isinstance(r, list) else [])}

def gh_ensure_labels(desired):
    ex = gh_list_labels()
    created = 0
    for name, color in desired.items():
        if name not in ex:
            gh_api("POST", "labels", {"name":name,"color":color,"description":f"[MaxOS AI] {name}"})
            created += 1
    if created: log(f"Labels: {created} créé(s)")

STANDARD_LABELS = {
    "ai-reviewed":"0075ca","ai-approved":"0e8a16","ai-rejected":"b60205",
    "ai-generated":"8b5cf6","needs-fix":"e4e669","needs-review":"fbca04",
    "bug":"d73a4a","enhancement":"a2eeef","question":"d876e3","stale":"eeeeee",
    "kernel":"5319e7","driver":"1d76db","app":"0052cc","boot":"e11d48",
    "security":"b91c1c","documentation":"0ea5e9","good-first-issue":"7057ff",
}

def gh_ensure_milestone(title, description=""):
    r = gh_api("GET", "milestones?state=open&per_page=30")
    for m in (r if isinstance(r, list) else []):
        if m.get("title") == title: return m.get("number")
    r2 = gh_api("POST", "milestones", {"title":title,"description":description or f"[AI] {title}"})
    return r2.get("number") if r2 else None

def gh_list_releases(n=10):
    r = gh_api("GET", f"releases?per_page={n}")
    return r if isinstance(r, list) else []

def gh_create_release(tag, name, body, pre=False):
    r = gh_api("POST", "releases", {
        "tag_name": tag, "target_commitish": "main",
        "name": name, "body": body, "draft": False, "prerelease": pre,
    })
    return r.get("html_url") if r and "html_url" in r else None

def gh_repo_info():
    repo  = gh_api("GET", "") or {}
    langs = gh_api("GET", "languages") or {}
    return {
        "stars":    repo.get("stargazers_count", 0),
        "forks":    repo.get("forks_count", 0),
        "size_kb":  repo.get("size", 0),
        "languages": langs,
        "default_branch": repo.get("default_branch", "main"),
    }

def gh_compare(base, head):
    r = gh_api("GET", f"compare/{base}...{head}")
    return r if isinstance(r, dict) else {}

# ─── GIT ──────────────────────────────────────────────────────────────────────
def git_cmd(args, timeout=60):
    try:
        r = subprocess.run(["git"]+args, cwd=REPO_PATH,
                           capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"timeout {timeout}s"
    except Exception as e:
        return False, "", str(e)

def git_sha(short=True):
    ok, out, _ = git_cmd(["rev-parse","HEAD"])
    if not ok: return ""
    s = out.strip()
    return s[:7] if short else s

def git_current_branch():
    ok, out, _ = git_cmd(["branch","--show-current"])
    return out.strip() if ok else "main"

def git_push(task_name, files, desc, model):
    if not files: return True, None, None

    dirs   = set(f.split("/")[0] for f in files if "/" in f)
    pmap   = {"kernel":"kernel","drivers":"driver","boot":"boot","ui":"ui","apps":"feat"}
    prefix = next((pmap[d] for d in pmap if d in dirs), "feat")
    fshort = ", ".join(os.path.basename(f) for f in files[:3])
    if len(files) > 3: fshort += f" +{len(files)-3}"
    short  = f"{prefix}: {task_name[:50]} [{fshort}]"
    body   = f"{short}\n\nFiles: {', '.join(files[:10])}\nModel: {model}\nArch: x86-32 bare metal\n\n[skip ci]"

    git_cmd(["add","-A"])
    ok, out, err = git_cmd(["commit","-m",body])
    if not ok:
        if "nothing to commit" in (out+err):
            log("Git: rien à committer")
            return True, None, None
        log(f"Commit KO: {err[:250]}", "ERROR")
        return False, None, None

    sha = git_sha()
    ok2, _, e2 = git_cmd(["push","--set-upstream","origin",git_current_branch()])
    if not ok2:
        git_cmd(["pull","--rebase","--autostash"])
        ok2, _, e2 = git_cmd(["push"])
        if not ok2:
            log(f"Push KO: {e2[:250]}", "ERROR")
            return False, None, None

    _CYCLE_STATS["total_commits"] += 1
    log(f"Push OK: {sha} — {short[:60]}", "GIT")
    return True, sha, short

# ─── BUILD ───────────────────────────────────────────────────────────────────
_ERR_RE = re.compile(
    r"(?:error:|fatal error:|fatal:|undefined reference|cannot find|no such file"
    r"|\*\*\* \[|Error \d+\s*$|FAILED\s*$|nasm:.*error|ld:.*error"
    r"|collect2: error|linker command failed|multiple definition|duplicate symbol"
    r"|identifier expected|expression syntax|undefined symbol|cannot open)",
    re.IGNORECASE
)

def parse_errs(log_text):
    seen, result = set(), []
    for line in log_text.split("\n"):
        s = line.strip()
        if s and _ERR_RE.search(s) and s not in seen:
            seen.add(s)
            result.append(s[:140])
    return result[:35]

def make_build(incremental=False):
    if not incremental:
        subprocess.run(["make","clean"], cwd=REPO_PATH, capture_output=True, timeout=30)
    t0 = time.time()
    try:
        r = subprocess.run(["make","-j2"], cwd=REPO_PATH,
                           capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        log("Build TIMEOUT 180s", "ERROR")
        return False, "TIMEOUT", ["Build timeout"]

    el   = round(time.time() - t0, 1)
    ok   = r.returncode == 0
    lt   = r.stdout + r.stderr
    errs = parse_errs(lt)

    log(f"Build {'OK' if ok else f'FAIL ({len(errs)} err)'} {el}s", "BUILD")
    for e in errs[:6]: log(f"  >> {e[:115]}", "BUILD")

    if ok:
        _CYCLE_STATS["builds_ok"] += 1
        disc_log("🔨 Build ✅", f"`{el}s`", 0x00CC44)
    else:
        _CYCLE_STATS["builds_fail"] += 1
        es = "\n".join(f"`{e[:85]}`" for e in errs[:5])
        disc_log(f"🔨 Build ❌ ({len(errs)} err)", f"`{el}s`\n{es}", 0xFF2200)

    return ok, lt, errs

# ─── FILE DISCOVERY ──────────────────────────────────────────────────────────
SKIP_DIRS  = {".git","build","__pycache__",".github","ai_dev",".vscode","node_modules"}
SKIP_FILES = {".DS_Store","Thumbs.db"}
SRC_EXTS   = {".c",".h",".asm",".ld",".s"}

CANONICAL_FILES = [
    "boot/boot.asm",
    "kernel/kernel_entry.asm",
    "kernel/kernel.c",
    "kernel/io.h",
    "kernel/idt.h",
    "kernel/idt.c",
    "kernel/isr.asm",
    "kernel/timer.h",
    "kernel/timer.c",
    "kernel/memory.h",
    "kernel/memory.c",
    "drivers/screen.h",
    "drivers/screen.c",
    "drivers/keyboard.h",
    "drivers/keyboard.c",
    "drivers/vga.h",
    "drivers/vga.c",
    "apps/terminal.h",
    "apps/terminal.c",
    "Makefile",
    "linker.ld",
]

def discover_files():
    found = []
    for root, dirs, files in os.walk(REPO_PATH):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f in SKIP_FILES: continue
            ext = os.path.splitext(f)[1]
            if ext in SRC_EXTS or f == "Makefile":
                rel = os.path.relpath(os.path.join(root,f), REPO_PATH).replace("\\","/")
                found.append(rel)
    return sorted(found)

def read_all(force=False):
    af = sorted(set(CANONICAL_FILES + discover_files()))
    h  = hashlib.md5()
    for f in af:
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            try:
                st = os.stat(p)
                h.update(f"{f}:{st.st_mtime:.3f}:{st.st_size}".encode())
            except OSError: pass
    cur = h.hexdigest()
    if not force and SOURCE_CACHE["hash"] == cur and SOURCE_CACHE["data"]:
        return SOURCE_CACHE["data"]
    src = {}
    for f in af:
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            try:
                with open(p,"r",encoding="utf-8",errors="ignore") as fh:
                    src[f] = fh.read()
            except: src[f] = None
        else:
            src[f] = None
    SOURCE_CACHE["hash"] = cur
    SOURCE_CACHE["data"] = src
    return src

def proj_stats(sources):
    files = sum(1 for c in sources.values() if c)
    lines = sum(c.count("\n") for c in sources.values() if c)
    chars = sum(len(c) for c in sources.values() if c)
    by_ext = defaultdict(int)
    for f, c in sources.items():
        if c:
            ext = os.path.splitext(f)[1] or "other"
            by_ext[ext] += 1
    return {"files":files,"lines":lines,"chars":chars,"by_ext":dict(by_ext)}

def build_ctx(sources, max_chars=38000):
    lines = ["=== CODE SOURCE MAXOS ===\n\nFICHIERS PRÉSENTS:\n"]
    for f, c in sources.items():
        lines.append(f"  {'✅' if c else '❌'} {f} ({len(c) if c else 0} chars)\n")
    lines.append("\n")
    ctx  = "".join(lines)
    used = len(ctx)
    prio = ["kernel/kernel.c","kernel/kernel_entry.asm","kernel/io.h",
            "Makefile","linker.ld","drivers/screen.h","drivers/keyboard.h"]
    done = set()
    for f in prio:
        c = sources.get(f,"")
        if not c: continue
        block = f"{'='*50}\nFICHIER: {f}\n{'='*50}\n{c}\n\n"
        if used + len(block) > max_chars:
            ctx += f"[{f}: {len(c)} chars — tronqué]\n"; done.add(f); continue
        ctx += block; used += len(block); done.add(f)
    for f, c in sources.items():
        if f in done or not c: continue
        block = f"{'='*50}\nFICHIER: {f}\n{'='*50}\n{c}\n\n"
        if used + len(block) > max_chars:
            ctx += f"[{f}: {len(c)} chars — tronqué]\n"; continue
        ctx += block; used += len(block)
    return ctx

def analyze_quality(sources):
    bad_inc = ["stddef.h","string.h","stdlib.h","stdio.h",
               "stdint.h","stdbool.h","stdarg.h","stdnoreturn.h"]
    bad_sym = ["size_t","NULL","bool","true","false",
               "uint32_t","uint8_t","uint16_t","int32_t",
               "malloc","free","calloc","realloc",
               "memset","memcpy","memmove","strlen","strcpy","strcat",
               "printf","sprintf","fprintf","puts"]
    violations = []
    cf = af = 0
    for fname, content in sources.items():
        if not content: continue
        if fname.endswith((".c",".h")):
            cf += 1
            for i, line in enumerate(content.split("\n"), 1):
                s = line.strip()
                if s.startswith(("//","/*","*","#pragma")): continue
                for inc in bad_inc:
                    if f"#include <{inc}>" in line or f'#include "{inc}"' in line:
                        violations.append(f"{fname}:{i} [INC] {inc}")
                for sym in bad_sym:
                    if re.search(r"\b"+re.escape(sym)+r"\b", line):
                        violations.append(f"{fname}:{i} [SYM] {sym}"); break
        elif fname.endswith((".asm",".s")):
            af += 1
    score = max(0, 100 - len(violations) * 3)
    return {"score":score,"violations":violations[:35],"c_files":cf,"asm_files":af}

# ─── FILE PARSING ─────────────────────────────────────────────────────────────
FILE_START_RE = re.compile(
    r"(?:={3,}|-{3,})\s*FILE\s*:\s*[`'\"]?([A-Za-z0-9_./@-][A-Za-z0-9_./@ -]*?)[`'\"]?\s*(?:={3,}|-{3,})",
    re.IGNORECASE
)
FILE_END_RE = re.compile(
    r"(?:={3,}|-{3,})\s*END\s*(?:FILE)?\s*(?:={3,}|-{3,})",
    re.IGNORECASE
)
FILE_DELETE_RE = re.compile(
    r"(?:={3,}|-{3,})\s*DELETE\s*:\s*[`'\"]?([A-Za-z0-9_./@-][A-Za-z0-9_./@ -]*?)[`'\"]?\s*(?:={3,}|-{3,})",
    re.IGNORECASE
)

def parse_ai_files(resp):
    files  = {}
    to_del = []
    cur    = None
    lines  = []
    in_f   = False

    for raw_line in resp.split("\n"):
        s = raw_line.strip()
        del_m = FILE_DELETE_RE.match(s)
        if del_m:
            fn = del_m.group(1).strip()
            if fn: to_del.append(fn)
            continue
        start_m = FILE_START_RE.match(s)
        if start_m:
            if in_f and cur and lines: _commit_file(files, cur, lines)
            fn = start_m.group(1).strip()
            if fn and not fn.startswith("-") and len(fn) > 1:
                cur = fn; lines = []; in_f = True
            continue
        if FILE_END_RE.match(s) and in_f:
            if cur and lines: _commit_file(files, cur, lines)
            cur = None; lines = []; in_f = False
            continue
        if in_f: lines.append(raw_line)

    if in_f and cur and lines: _commit_file(files, cur, lines)
    if not files and not to_del:
        log(f"Parse: aucun fichier. Début: {resp[:200]}", "WARN")
    return files, to_del

def _commit_file(files_dict, path, lines):
    path    = path.strip().strip("`'\"")
    content = "\n".join(lines).strip()
    for fence in ("```c","```asm","```nasm","```makefile","```ld","```bash","```text","```"):
        if content.startswith(fence):
            content = content[len(fence):].lstrip("\n"); break
    if content.endswith("```"):
        content = content[:-3].rstrip("\n")
    content = content.strip()
    if content and len(content) > 5:
        files_dict[path] = content
        log(f"Parsé: {path} ({len(content):,}c)")
    else:
        log(f"Parsé vide ignoré: {path}", "WARN")

def write_files(files):
    written   = []
    repo_real = os.path.realpath(REPO_PATH) + os.sep
    for path, content in files.items():
        path = path.strip().strip("/").replace("\\","/")
        full = os.path.realpath(os.path.join(REPO_PATH, path))
        if not (full + os.sep).startswith(repo_real):
            log(f"Path traversal bloqué: {path}", "ERROR"); continue
        # Validate content
        if not content or len(content) < 5:
            log(f"Contenu trop court ignoré: {path}", "WARN"); continue
        if content.count("...") > 5 and len(content) < 100:
            log(f"Placeholder détecté ignoré: {path}", "WARN"); continue
        parent = os.path.dirname(full)
        if parent and parent != REPO_PATH:
            os.makedirs(parent, exist_ok=True)
        try:
            with open(full,"w",encoding="utf-8",newline="\n") as f:
                f.write(content)
            written.append(path)
            log(f"Écrit: {path} ({len(content):,}c)")
        except Exception as e:
            log(f"Erreur écriture {path}: {e}", "ERROR")
    SOURCE_CACHE["hash"] = None
    return written

def del_files(paths):
    deleted   = []
    repo_real = os.path.realpath(REPO_PATH) + os.sep
    for path in paths:
        path = path.strip().strip("/")
        full = os.path.realpath(os.path.join(REPO_PATH, path))
        if not (full+os.sep).startswith(repo_real):
            log(f"Delete path traversal bloqué: {path}", "ERROR"); continue
        if os.path.exists(full) and os.path.isfile(full):
            os.remove(full); deleted.append(path)
            log(f"Supprimé: {path}")
    SOURCE_CACHE["hash"] = None
    return deleted

def backup(paths):
    bak = {}
    for p in paths:
        full = os.path.join(REPO_PATH, p)
        if os.path.exists(full) and os.path.isfile(full):
            try:
                with open(full,"r",encoding="utf-8",errors="ignore") as f:
                    bak[p] = f.read()
            except: pass
    return bak

def restore(bak):
    if not bak: return
    for p, c in bak.items():
        full   = os.path.join(REPO_PATH, p)
        parent = os.path.dirname(full)
        if parent: os.makedirs(parent, exist_ok=True)
        try:
            with open(full,"w",encoding="utf-8",newline="\n") as f:
                f.write(c)
        except Exception as e:
            log(f"Erreur restore {p}: {e}", "ERROR")
    log(f"Restauré {len(bak)} fichier(s)")
    SOURCE_CACHE["hash"] = None

# ─── OS CONSTANTS ─────────────────────────────────────────────────────────────
OS_MISSION = (
    "MISSION MaxOS: OS bare metal x86 complet, moderne, stable.\n"
    "PROGRESSION: Boot→IDT+PIC→Timer PIT→Mémoire bitmap→"
    "VGA mode13h→Clavier IRQ→Terminal→FAT12→GUI desktop"
)

RULES = """╔══ RÈGLES BARE METAL x86 — VIOLATIONS = ÉCHEC BUILD ══╗
║ INCLUDES INTERDITS: stddef.h string.h stdlib.h stdio.h║
║   stdint.h stdbool.h stdarg.h stdnoreturn.h            ║
║ SYMBOLES INTERDITS: size_t NULL bool true false        ║
║   uint32_t uint8_t uint16_t int32_t                    ║
║   malloc free calloc realloc                           ║
║   memset memcpy memmove strlen strcpy strcat           ║
║   printf sprintf fprintf puts                          ║
║ REMPLACEMENTS: size_t→unsigned int  NULL→0             ║
║   bool/true/false→int/1/0  uint32_t→unsigned int      ║
║   uint8_t→unsigned char  uint16_t→unsigned short      ║
║ TOOLCHAIN:                                             ║
║   GCC: -m32 -ffreestanding -fno-builtin               ║
║        -nostdlib -nostdinc -fno-pic -fno-pie           ║
║   NASM: -f elf (→.o) | -f bin (boot.bin)              ║
║   LD: ld -m elf_i386 -T linker.ld --oformat binary    ║
║ RÈGLES CRITIQUES:                                      ║
║   • kernel/io.h: SEUL fichier avec outb/inb            ║
║     static inline — JAMAIS redéfinir ailleurs          ║
║   • isr.asm: PAS de %macro/%rep pour stubs             ║
║     Écrire isr0:...isr47: MANUELLEMENT ligne/ligne     ║
║   • kernel_entry.asm: global _stack_top EN PREMIER     ║
║     resb 16384, puis global kernel_main                ║
║   • Tout .c nouveau → dans Makefile OBJS               ║
║   • ZÉRO commentaire dans le code généré               ║
║   • Chaque .c doit #include son propre .h              ║
║   • os.img DOIT être créé par le Makefile              ║
╚════════════════════════════════════════════════════════╝"""

# ─── MAKEFILE TEMPLATE ───────────────────────────────────────────────────────
MAKEFILE_TEMPLATE = """AS     = nasm
CC     = gcc
LD     = ld
CFLAGS = -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie -Wall -O2
LFLAGS = -m elf_i386 -T linker.ld --oformat binary
BFLAGS = -f bin
EFLAGS = -f elf

BUILD  = build
BOOT   = boot/boot.asm
KERNEL_ENTRY = kernel/kernel_entry.asm

OBJS = \\
\t$(BUILD)/kernel.o \\
\t$(BUILD)/idt.o \\
\t$(BUILD)/isr.o \\
\t$(BUILD)/timer.o \\
\t$(BUILD)/memory.o \\
\t$(BUILD)/screen.o \\
\t$(BUILD)/keyboard.o \\
\t$(BUILD)/vga.o \\
\t$(BUILD)/terminal.o \\
\t$(BUILD)/notepad.o \\
\t$(BUILD)/sysinfo.o \\
\t$(BUILD)/about.o

.PHONY: all clean

all: os.img

$(BUILD):
\tmkdir -p $(BUILD)

$(BUILD)/boot.bin: $(BOOT) | $(BUILD)
\t$(AS) $(BFLAGS) $< -o $@

$(BUILD)/kernel_entry.o: $(KERNEL_ENTRY) | $(BUILD)
\t$(AS) $(EFLAGS) $< -o $@

$(BUILD)/isr.o: kernel/isr.asm | $(BUILD)
\t$(AS) $(EFLAGS) $< -o $@

$(BUILD)/kernel.o: kernel/kernel.c | $(BUILD)
\t$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/idt.o: kernel/idt.c | $(BUILD)
\t$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/timer.o: kernel/timer.c | $(BUILD)
\t$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/memory.o: kernel/memory.c | $(BUILD)
\t$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/screen.o: drivers/screen.c | $(BUILD)
\t$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/keyboard.o: drivers/keyboard.c | $(BUILD)
\t$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/vga.o: drivers/vga.c | $(BUILD)
\t$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/terminal.o: apps/terminal.c | $(BUILD)
\t$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/notepad.o: apps/notepad.c | $(BUILD)
\t$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/sysinfo.o: apps/sysinfo.c | $(BUILD)
\t$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/about.o: apps/about.c | $(BUILD)
\t$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/kernel.bin: $(BUILD)/kernel_entry.o $(OBJS) | $(BUILD)
\t$(LD) $(LFLAGS) $^ -o $@

os.img: $(BUILD)/boot.bin $(BUILD)/kernel.bin
\tdd if=/dev/zero of=os.img bs=512 count=2880
\tdd if=$(BUILD)/boot.bin of=os.img conv=notrunc
\tdd if=$(BUILD)/kernel.bin of=os.img seek=1 conv=notrunc

clean:
\trm -rf $(BUILD) os.img
"""

# ─── DEFAULT PLAN ─────────────────────────────────────────────────────────────
def default_plan():
    return {
        "score_actuel":  35,
        "niveau_os":     "Prototype bare metal",
        "fonctionnalites_presentes": ["Boot x86","VGA texte 80x25","Clavier PS/2 polling"],
        "fonctionnalites_manquantes_critiques": ["IDT+PIC","Timer PIT","Mémoire bitmap"],
        "prochaine_milestone": "Kernel stable IDT+Timer+Memory",
        "plan_ameliorations": [
            {
                "nom":                  "Makefile + linker.ld corrects avec os.img",
                "priorite":             "CRITIQUE",
                "categorie":            "build",
                "fichiers_a_modifier":  ["Makefile","linker.ld"],
                "fichiers_a_creer":     [],
                "fichiers_a_supprimer": [],
                "description": (
                    "Makefile doit produire os.img: dd if=/dev/zero of=os.img bs=512 count=2880; "
                    "dd if=build/boot.bin of=os.img conv=notrunc; "
                    "dd if=build/kernel.bin of=os.img seek=1 conv=notrunc. "
                    "linker.ld: ENTRY(kmain) OUTPUT_FORMAT(binary) "
                    "SECTIONS { .text 0x1000: { *(.text) } .data: { *(.data) } .bss: { *(.bss) } }"
                ),
                "impact_attendu": "os.img bootable généré automatiquement",
                "complexite":     "BASSE",
            },
            {
                "nom":                  "kernel/io.h + kernel/idt.c + kernel/isr.asm complets",
                "priorite":             "CRITIQUE",
                "categorie":            "kernel",
                "fichiers_a_modifier":  ["kernel/kernel.c","Makefile"],
                "fichiers_a_creer":     ["kernel/io.h","kernel/idt.h","kernel/idt.c","kernel/isr.asm"],
                "fichiers_a_supprimer": [],
                "description": (
                    "kernel/io.h: #ifndef IO_H #define IO_H "
                    "static inline void outb(unsigned short p,unsigned char v){asm volatile(\"outb %0,%1\"::\"a\"(v),\"Nd\"(p));} "
                    "static inline unsigned char inb(unsigned short p){unsigned char v;asm volatile(\"inb %1,%0\":\"=a\"(v):\"Nd\"(p));return v;} "
                    "#endif "
                    "kernel/idt.h: struct IDTEntry{unsigned short bl;unsigned short sel;unsigned char z;unsigned char f;unsigned short bh;}__attribute__((packed)); "
                    "struct IDTPtr{unsigned short lim;unsigned int base;}__attribute__((packed)); "
                    "void idt_init(void); void idt_set_gate(unsigned char n,unsigned int base,unsigned short sel,unsigned char flags); "
                    "kernel/idt.c: #include \"io.h\" #include \"idt.h\" "
                    "static struct IDTEntry idt[256]; static struct IDTPtr idtp; "
                    "idt_set_gate: idt[n].bl=base&0xFFFF;idt[n].sel=sel;idt[n].z=0;idt[n].f=flags;idt[n].bh=(base>>16)&0xFFFF; "
                    "idt_init: configure PIC remap(outb 0x20/0xA0 séquence ICW1-4), "
                    "fill idt[0..47] avec extern void isrN(), lidt. "
                    "kernel/isr.asm: BITS 32 section .text "
                    "Écrire EXPLICITEMENT isr0: push byte 0 push byte 0 jmp isr_common "
                    "isr1: push byte 0 push byte 1 jmp isr_common ... jusqu'à isr47. "
                    "Exceptions avec errcode(8,10-14,17): omit push byte 0. "
                    "isr_common: pushad push ds push es push fs push gs "
                    "mov ax,0x10 mov ds,ax mov es,ax "
                    "push esp call isr_handler add esp,4 "
                    "pop gs pop fs pop es pop ds popad add esp,8 iret "
                    "extern isr_handler global isr0..isr47"
                ),
                "impact_attendu": "IDT fonctionnelle, pas de triple fault",
                "complexite":     "HAUTE",
            },
            {
                "nom":                  "kernel/timer.c + kernel/memory.c fonctionnels",
                "priorite":             "HAUTE",
                "categorie":            "kernel",
                "fichiers_a_modifier":  ["kernel/kernel.c","Makefile"],
                "fichiers_a_creer":     ["kernel/timer.h","kernel/timer.c","kernel/memory.h","kernel/memory.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "timer.h: void timer_init(void); unsigned int timer_ticks(void); void sleep_ms(unsigned int ms); "
                    "timer.c: volatile unsigned int g_ticks=0; "
                    "irq0 handler: g_ticks++; outb(0x20,0x20); "
                    "timer_init: diviseur=11931; outb(0x43,0x36); outb(0x40,div&0xFF); outb(0x40,(div>>8)&0xFF); "
                    "idt_set_gate(32,(unsigned int)irq0,0x08,0x8E); outb(0x21,inb(0x21)&~0x01); "
                    "sleep_ms: unsigned int end=g_ticks+(ms/10); while(g_ticks<end){asm volatile(\"hlt\");} "
                    "memory.h: void mem_init(unsigned int start,unsigned int end); "
                    "unsigned int mem_alloc(void); void mem_free(unsigned int addr); "
                    "memory.c: #define PAGE_SIZE 4096 #define MAX_PAGES 8192 "
                    "static unsigned int bitmap[MAX_PAGES/32]; "
                    "mem_init: calcule pages=(end-start)/4096; clear bitmap. "
                    "mem_alloc: find bit=0, set, return addr. "
                    "mem_free: clear bit pour addr."
                ),
                "impact_attendu": "Timer 100Hz + allocateur pages 4KB",
                "complexite":     "HAUTE",
            },
            {
                "nom":                  "Terminal 25 commandes + drivers complets",
                "priorite":             "HAUTE",
                "categorie":            "app",
                "fichiers_a_modifier":  ["apps/terminal.c","apps/terminal.h","drivers/keyboard.c","kernel/kernel.c"],
                "fichiers_a_creer":     [],
                "fichiers_a_supprimer": [],
                "description": (
                    "25 commandes: help ver mem uptime cls echo reboot halt color calc about "
                    "credits ps sysinfo license time date clear history env set beep disk cpu. "
                    "Historique 32 entrées flèche haut/bas. "
                    "keyboard.c: IRQ-driven via IDT gate 33; scancode→ASCII FR layout. "
                    "Signatures: tm_init() tm_draw() tm_key(unsigned char k) tm_run(). "
                    "ZÉRO stdlib."
                ),
                "impact_attendu": "Terminal complet type cmd.exe",
                "complexite":     "MOYENNE",
            },
        ],
    }

# ─── JSON PARSING ─────────────────────────────────────────────────────────────
def _parse_json_robust(resp):
    if not resp: return None
    clean = resp.strip()
    if clean.startswith("```"):
        lines = clean.split("\n")
        end   = -1 if lines[-1].strip() == "```" else len(lines)
        clean = "\n".join(lines[1:end]).strip()
    i = clean.find("{"); j = clean.rfind("}") + 1
    if i < 0 or j <= i: return None
    candidate = clean[i:j]
    try: return json.loads(candidate)
    except: pass
    fixed = re.sub(r',\s*([}\]])', r'\1', candidate)
    try: return json.loads(fixed)
    except: pass
    fixed2 = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r'\\\\', candidate)
    try: return json.loads(fixed2)
    except: return None

# ─── PHASE ANALYSE ────────────────────────────────────────────────────────────
def phase_analyse(context, stats):
    log("=== PHASE 1: ANALYSE PROJET ===")
    disc_now("🔍 Analyse en cours",
             f"`{stats['files']}` fichiers | `{stats['lines']:,}` lignes | `{stats['chars']:,}` chars",
             0x5865F2)

    prompt = (
        f"Tu es un expert OS bare metal x86. Analyse ce projet et retourne UNIQUEMENT du JSON valide.\n\n"
        f"{RULES}\n\n{OS_MISSION}\n\n"
        f"CONTEXT:\n{context[:18000]}\n\n"
        f"STATS: {stats['files']} fichiers, {stats['lines']} lignes\n\n"
        "Retourne UNIQUEMENT ce JSON (commence par { sans aucun texte avant):\n"
        '{"score_actuel":35,"niveau_os":"desc","fonctionnalites_presentes":["f1"],'
        '"fonctionnalites_manquantes_critiques":["f2"],"prochaine_milestone":"m",'
        '"plan_ameliorations":[{"nom":"N","priorite":"CRITIQUE","categorie":"kernel",'
        '"fichiers_a_modifier":["f"],"fichiers_a_creer":["g"],"fichiers_a_supprimer":[],'
        '"description":"specs","impact_attendu":"r","complexite":"HAUTE"}]}'
    )

    resp   = ai_call(prompt, max_tokens=3000, timeout=70, tag="analyse")
    if not resp:
        log("Analyse IA indisponible → plan défaut", "WARN")
        return default_plan()

    result = _parse_json_robust(resp)
    if result and isinstance(result.get("plan_ameliorations"), list) and result["plan_ameliorations"]:
        nb    = len(result["plan_ameliorations"])
        score = result.get("score_actuel","?")
        log(f"Analyse OK: score={score} | {nb} tâche(s)", "OK")
        return result

    log("JSON analyse invalide → plan défaut", "WARN")
    return default_plan()

# ─── TASK CONTEXT ─────────────────────────────────────────────────────────────
def task_ctx(task, sources):
    needed = set()
    needed.update(task.get("fichiers_a_modifier",[]))
    needed.update(task.get("fichiers_a_creer",[]))
    for f in list(needed):
        if f.endswith(".c"):   needed.add(f.replace(".c",".h"))
        elif f.endswith(".h"): needed.add(f.replace(".h",".c"))

    always = ["kernel/kernel.c","kernel/kernel_entry.asm","kernel/io.h",
              "Makefile","linker.ld","drivers/screen.h","drivers/keyboard.h"]
    needed.update(always)

    ctx  = ""; used = 0
    for f in sorted(needed):
        c = sources.get(f,"")
        if c:
            content_to_show = c if len(c) <= 12000 else c[:12000] + "\n[... TRONQUÉ ...]"
            block = f"--- {f} ---\n{content_to_show}\n\n"
        else:
            block = f"--- {f} ---\n[FICHIER À CRÉER]\n\n"
        if used + len(block) > 24000:
            ctx += f"[{f}: tronqué]\n"; continue
        ctx += block; used += len(block)
    return ctx

def impl_prompt(task, ctx):
    nom  = task.get("nom","?")
    cat  = task.get("categorie","?")
    cx   = task.get("complexite","MOYENNE")
    desc = task.get("description","")
    fmod = task.get("fichiers_a_modifier",[])
    fnew = task.get("fichiers_a_creer",[])
    fdel = task.get("fichiers_a_supprimer",[])

    return (
        f"{RULES}\n\n"
        f"{'='*60}\nTÂCHE: {nom}\nCATÉGORIE: {cat} | COMPLEXITÉ: {cx}\n"
        f"FICHIERS À MODIFIER: {fmod}\nFICHIERS À CRÉER: {fnew}\nFICHIERS À SUPPRIMER: {fdel}\n"
        f"{'='*60}\n\nSPÉCIFICATIONS:\n{desc}\n\nCODE EXISTANT:\n{ctx}\n\n"
        f"{'='*60}\nCONTRAINTES ABSOLUES:\n"
        "1. isr.asm: JAMAIS %macro/%rep — isr0:...isr47: EXPLICITEMENT un par un\n"
        "2. outb/inb: UNIQUEMENT dans kernel/io.h static inline\n"
        "   Autres fichiers: #include \"kernel/io.h\" (chemin RELATIF à la racine repo)\n"
        "3. kernel_entry.asm: 'global _stack_top' EN PREMIER\n"
        "4. Tout nouveau .c → Makefile OBJS\n"
        "5. os.img DOIT être créé par la règle 'all' du Makefile via dd\n"
        "6. ZÉRO commentaire, ZÉRO placeholder, code 100% complet\n"
        "7. Utiliser des chemins d'include COHÉRENTS avec le Makefile\n\n"
        "FORMAT OBLIGATOIRE:\n"
        "=== FILE: chemin/relatif/fichier.ext ===\n"
        "[code complet]\n"
        "=== END FILE ===\n\n"
        "GÉNÈRE MAINTENANT:"
    )

# ─── AUTO FIX ─────────────────────────────────────────────────────────────────
def auto_fix(build_log, errs, gen_files, bak, model, max_att=4):
    log(f"Auto-fix: {len(errs)} erreur(s)", "BUILD")
    _CYCLE_STATS["auto_fixes"] += 1
    cur_log  = build_log
    cur_errs = errs

    for att in range(1, max_att + 1):
        # If 0 errors but build still failed, something else is wrong
        if not cur_errs:
            log(f"Fix {att}: 0 erreurs parsées mais build fail — arrêt", "WARN")
            break

        log(f"Fix {att}/{max_att} — {len(cur_errs)} err", "BUILD")
        disc_log(f"🔧 Fix {att}/{max_att}",
                 f"`{len(cur_errs)}` erreur(s)\n" +
                 "\n".join(f"`{e[:60]}`" for e in cur_errs[:3]), 0x00AAFF)

        curr_files = {}
        for p in gen_files:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp) and os.path.isfile(fp):
                try:
                    with open(fp,"r",encoding="utf-8",errors="ignore") as f:
                        content = f.read()
                        # Provide full content but note if large
                        curr_files[p] = content[:14000]
                except: pass

        file_ctx = "".join(f"--- {p} ---\n{c}\n\n" for p, c in curr_files.items())
        err_str  = "\n".join(cur_errs[:20])
        log_tail = cur_log[-3000:] if len(cur_log) > 3000 else cur_log

        # Smart diagnostics
        diag = []
        if "multiple definition" in err_str and ("outb" in err_str or "inb" in err_str):
            diag.append("SOLUTION: outb/inb UNIQUEMENT dans kernel/io.h — retirer des autres fichiers")
        if "%rep" in err_str or "%macro" in err_str:
            diag.append("SOLUTION: Écrire isr0:...isr47: MANUELLEMENT, PAS de %macro/%rep")
        if "undefined reference to `isr" in err_str:
            diag.append("SOLUTION: Vérifier que isr.asm déclare 'global isr0' ... 'global isr47' et est dans Makefile")
        if "Error 127" in err_str:
            diag.append("SOLUTION: Commande introuvable dans Makefile — vérifier nasm/gcc dans PATH et règles Makefile")
        if "No such file or directory" in err_str:
            paths_missing = re.findall(r"fatal error: ([^\s:]+):", err_str)
            if paths_missing:
                diag.append(f"SOLUTION: Fichiers manquants: {paths_missing[:5]} — corriger les #include ou créer les fichiers")
        if "kernel_main" in err_str and "multiple definition" in err_str:
            diag.append("SOLUTION: kernel_main doit être dans UN SEUL fichier .c — kernel_entry.asm appelle kmain")
        if "linker script file" in err_str and "multiple times" in err_str:
            diag.append("SOLUTION: linker.ld ne doit apparaître qu'UNE FOIS dans la commande ld du Makefile")
        if "os.img" not in err_str and not any("os.img" in p for p in gen_files):
            diag.append("RAPPEL: Le Makefile DOIT créer os.img via dd après le build")

        prompt = (
            f"{RULES}\n\n"
            f"ERREURS:\n```\n{err_str}\n```\n\n"
            f"LOG BUILD (fin):\n```\n{log_tail}\n```\n\n"
            f"DIAGNOSTICS:\n" + "\n".join(f"⚡ {d}" for d in diag) + "\n\n"
            f"FICHIERS ACTUELS:\n{file_ctx}\n\n"
            "CORRIGER TOUTES LES ERREURS. Code 100% complet, ZÉRO commentaire.\n"
            "FORMAT:\n=== FILE: fichier ===\n[code]\n=== END FILE ==="
        )

        resp = ai_call(prompt, max_tokens=32768, timeout=130, tag=f"fix/{att}")
        if not resp:
            time.sleep(min(8*(2**(att-1)), 45))
            continue

        new_files, _ = parse_ai_files(resp)
        if not new_files:
            log(f"Fix {att}: parse vide", "WARN")
            time.sleep(min(5*(2**(att-1)), 30))
            continue

        write_files(new_files)
        ok, cur_log, cur_errs = make_build(incremental=False)

        if ok:
            m_u = alive()[0]["model"] if alive() else model
            git_push("fix: build", list(new_files.keys()), f"auto-fix {len(errs)}→0", m_u)
            disc_now("🔧 Fix ✅", f"**{len(errs)} err** → **0** en {att} tentative(s)", 0x00AAFF)
            _CYCLE_STATS["auto_fix_success"] += 1
            return True, {"attempts": att, "fixed_files": list(new_files.keys())}

        log(f"Fix {att}: {len(cur_errs)} erreur(s) restantes", "WARN")
        time.sleep(min(6*(2**(att-1)), 35))

    _CYCLE_STATS["auto_fix_fail"] += 1
    return False, {"attempts": max_att, "remaining_errors": cur_errs[:5]}

# ─── PRE-FLIGHT ───────────────────────────────────────────────────────────────
def pre_flight_check():
    log("Pre-flight: vérification build initial...", "BUILD")

    # Ensure Makefile creates os.img
    makefile_path = os.path.join(REPO_PATH, "Makefile")
    if os.path.exists(makefile_path):
        with open(makefile_path,"r") as f:
            mf = f.read()
        if "os.img" not in mf:
            log("Makefile sans os.img — injection du template", "WARN")
            with open(makefile_path,"w",newline="\n") as f:
                f.write(MAKEFILE_TEMPLATE)
    else:
        log("Makefile manquant — création du template", "WARN")
        os.makedirs(os.path.dirname(makefile_path), exist_ok=True)
        with open(makefile_path,"w",newline="\n") as f:
            f.write(MAKEFILE_TEMPLATE)

    ok, log_text, errs = make_build()
    if not ok:
        log(f"Pre-flight: build cassé ({len(errs)} err)", "WARN")
        disc_now("⚠️ Build pré-existant cassé",
                 f"`{len(errs)}` erreur(s)\n" + "\n".join(f"`{e[:75]}`" for e in errs[:4]),
                 0xFF6600)
        return False, errs
    # Check os.img was created
    img_path = os.path.join(REPO_PATH, "os.img")
    if not os.path.exists(img_path):
        log("os.img non créé par le build !", "WARN")
    else:
        log(f"os.img créé: {os.path.getsize(img_path)} bytes ✅", "OK")
    log("Pre-flight: build OK ✅", "OK")
    return True, []

# ─── IMPLEMENT TASK ───────────────────────────────────────────────────────────
def implement(task, sources, i, total):
    nom   = task.get("nom", f"Tâche {i}")
    cat   = task.get("categorie","?")
    prio  = task.get("priorite","?")
    cx    = task.get("complexite","MOYENNE")
    desc  = task.get("description","")
    f_mod = task.get("fichiers_a_modifier",[])
    f_new = task.get("fichiers_a_creer",[])
    model = alive()[0]["model"] if alive() else "?"

    log(f"\n{'='*56}\n[{i}/{total}] [{prio}] {nom}\n{'='*56}")

    disc_now(
        f"🚀 [{i}/{total}] {nom[:55]}",
        f"```\n{pbar(int((i-1)/total*100))}\n```\n{desc[:280]}",
        0xFFA500,
        [
            {"name":"🎯 Priorité",  "value":prio,  "inline":True},
            {"name":"📁 Catégorie", "value":cat,   "inline":True},
            {"name":"⚙️ Complexité","value":cx,    "inline":True},
            {"name":"📝 Modifier",  "value":"\n".join(f"`{f}`" for f in f_mod[:5]) or "—","inline":True},
            {"name":"✨ Créer",     "value":"\n".join(f"`{f}`" for f in f_new[:5]) or "—","inline":True},
            {"name":"🔑 Providers", "value":prov_summary()[:400],"inline":False},
        ]
    )

    t0      = time.time()
    ctx     = task_ctx(task, sources)
    max_tok = {"HAUTE":32768,"MOYENNE":24576,"BASSE":12288,"TRES HAUTE":32768}.get(cx, 24576)
    prompt  = impl_prompt(task, ctx)
    resp    = ai_call(prompt, max_tokens=max_tok, timeout=200, tag=f"impl/{nom[:16]}")
    elapsed = round(time.time() - t0, 1)

    if not resp:
        disc_now(f"❌ [{i}/{total}] {nom[:50]}",
                 f"Tous providers indisponibles après {elapsed}s", 0xFF4444)
        return False, [], [], {"nom":nom,"elapsed":elapsed,"result":"ai_fail","errors":[],"model":model}

    files, to_del = parse_ai_files(resp)

    if not files and not to_del:
        disc_now(f"❌ [{i}/{total}] {nom[:50]}",
                 f"Réponse {len(resp):,}c mais aucun fichier parsé", 0xFF6600,
                 [{"name":"Début","value":f"```\n{resp[:300]}\n```","inline":False}])
        return False, [], [], {"nom":nom,"elapsed":elapsed,"result":"parse_empty","errors":[],"model":model}

    disc_log(f"📁 {len(files)} fichier(s)",
             "\n".join(f"`{f}` → {len(c):,}c" for f, c in list(files.items())[:10]), 0x00AAFF)

    bak_f   = backup(list(files.keys()))
    written = write_files(files)
    deleted = del_files(to_del)

    if not written and not deleted:
        return False, [], [], {"nom":nom,"elapsed":elapsed,"result":"no_files_written","errors":[],"model":model}

    ok, build_log, errs = make_build()

    # Check os.img
    img_path = os.path.join(REPO_PATH, "os.img")
    img_ok   = os.path.exists(img_path) and os.path.getsize(img_path) > 0

    if ok:
        if not img_ok:
            log("Build OK mais os.img manquant — ajout cible dd au Makefile", "WARN")
            # Try to patch Makefile to add os.img
            _ensure_osimg_in_makefile()
            ok, build_log, errs = make_build()
            img_ok = os.path.exists(img_path)

        pushed, sha, commit_short = git_push(nom, written+deleted, desc, model)
        total_elapsed = round(time.time() - t0, 1)

        if pushed and sha:
            m = {"nom":nom,"elapsed":total_elapsed,"result":"success","sha":sha,
                 "files":written+deleted,"model":model,"fix_count":0,"img_ok":img_ok}
            fs_str = "\n".join(f"`{f}`" for f in (written+deleted)[:8]) or "—"
            disc_now(
                f"✅ [{i}/{total}] {nom[:50]}",
                f"```\n{pbar(int(i/total*100))}\n```\nCommit: `{sha}`\nos.img: {'✅' if img_ok else '❌'}",
                0x00FF88,
                [
                    {"name":"⏱️","value":f"{total_elapsed:.0f}s","inline":True},
                    {"name":"📁","value":str(len(written+deleted)),"inline":True},
                    {"name":"🤖","value":model[:30],"inline":True},
                    {"name":"📝 Liste","value":fs_str,"inline":False},
                ]
            )
            return True, written, deleted, m

        elif pushed and sha is None:
            disc_log(f"✅ [{i}/{total}] {nom[:50]} (déjà à jour)", "", 0x00AA44)
            return True, [], [], {"nom":nom,"elapsed":total_elapsed,"result":"success_no_change",
                                   "sha":git_sha(),"files":[],"model":model,"fix_count":0}
        else:
            restore(bak_f)
            return False, [], [], {"nom":nom,"elapsed":elapsed,"result":"push_fail","errors":[],"model":model}

    fixed, fix_meta = auto_fix(build_log, errs, list(files.keys()), bak_f, model)

    if fixed:
        total_elapsed = round(time.time() - t0, 1)
        fc   = fix_meta.get("attempts",0)
        img_ok = os.path.exists(img_path)
        m    = {"nom":nom,"elapsed":total_elapsed,"result":"success_after_fix",
                "sha":git_sha(),"files":written+deleted,"model":model,"fix_count":fc,"img_ok":img_ok}
        disc_now(
            f"✅ [{i}/{total}] {nom[:50]} (fix×{fc})",
            f"```\n{pbar(int(i/total*100))}\n```\nos.img: {'✅' if img_ok else '❌'}",
            0x00BB66,
            [{"name":"⏱️","value":f"{total_elapsed:.0f}s","inline":True},
             {"name":"🔧","value":f"{fc} fix","inline":True},
             {"name":"🤖","value":model[:30],"inline":True}]
        )
        return True, written, deleted, m

    restore(bak_f)
    for p in written:
        if p not in bak_f:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp) and os.path.isfile(fp):
                try: os.remove(fp)
                except: pass
    SOURCE_CACHE["hash"] = None
    total_elapsed = round(time.time() - t0, 1)
    remaining_errs = fix_meta.get("remaining_errors", errs[:5])
    es = "\n".join(f"`{e[:80]}`" for e in remaining_errs[:5])
    disc_now(
        f"❌ [{i}/{total}] {nom[:50]}",
        f"Build fail après {fix_meta.get('attempts',0)} fix(es) — restauré",
        0xFF4444,
        [{"name":"Erreurs","value":es[:900] or "?","inline":False},
         {"name":"⏱️","value":f"{total_elapsed:.0f}s","inline":True},
         {"name":"🔧","value":str(fix_meta.get("attempts",0)),"inline":True}]
    )
    return False, [], [], {"nom":nom,"elapsed":total_elapsed,"result":"build_fail",
                            "errors":remaining_errs[:5],"model":model}

def _ensure_osimg_in_makefile():
    """Patch Makefile to add os.img target if missing."""
    mf_path = os.path.join(REPO_PATH, "Makefile")
    if not os.path.exists(mf_path): return
    with open(mf_path,"r") as f:
        content = f.read()
    if "os.img" in content: return
    # Find the 'all' target and patch it
    patch = "\nos.img: $(BUILD)/boot.bin $(BUILD)/kernel.bin\n"
    patch += "\tdd if=/dev/zero of=os.img bs=512 count=2880\n"
    patch += "\tdd if=$(BUILD)/boot.bin of=os.img conv=notrunc\n"
    patch += "\tdd if=$(BUILD)/kernel.bin of=os.img seek=1 conv=notrunc\n"
    content = re.sub(r"(all\s*:.*?\n)", r"\1\n" + patch, content, count=1)
    with open(mf_path,"w",newline="\n") as f:
        f.write(content)
    SOURCE_CACHE["hash"] = None
    log("Makefile patché pour os.img")

# ─── ISSUE / PR / STALE HANDLERS ─────────────────────────────────────────────
BOT_LOGINS = frozenset({
    "MaxOS-AI-Bot","github-actions[bot]",
    "dependabot[bot]","maxos-ai[bot]","renovate[bot]",
})

def _bot_already_commented(n):
    comments = gh_issue_comments(n)
    return any(c.get("user",{}).get("login","") in BOT_LOGINS for c in (comments or []))

def handle_issues(ms_cache=None):
    if ms_cache is None: ms_cache = {}
    issues = gh_open_issues()
    if not issues: log("Issues: aucune"); return ms_cache
    log(f"Issues: {len(issues)} ouverte(s)")

    treated = 0
    for issue in issues[:10]:
        n      = issue.get("number")
        title  = issue.get("title","")
        author = issue.get("user",{}).get("login","")
        body_t = (issue.get("body","") or "")[:800]
        labels = [l.get("name","") for l in issue.get("labels",[])]

        if issue.get("state") != "open": continue
        if author in BOT_LOGINS: continue
        if _bot_already_commented(n): continue
        if not watchdog(): break

        log(f"Issue #{n}: {title[:65]}")

        prompt = (
            f"Bot GitHub de MaxOS, OS bare metal x86.\n"
            f"ISSUE #{n}\nTitre: {title}\nAuteur: {author}\nLabels: {', '.join(labels) or 'aucun'}\n"
            f"Corps:\n{body_t}\n\n"
            'Réponds UNIQUEMENT avec JSON valide:\n'
            '{"type":"bug|enhancement|question|invalid","priority":"critical|high|medium|low",'
            '"component":"kernel|driver|app|build|doc|other","labels_add":["bug"],'
            '"action":"respond|close|label_only","response":"réponse utile en français"}'
        )

        a = _parse_json_robust(ai_call(prompt, max_tokens=800, timeout=40, tag=f"issue/{n}"))
        if not a: continue

        action = a.get("action","label_only")
        lbl_add = [l for l in a.get("labels_add",[]) if l in STANDARD_LABELS]
        if "ai-reviewed" not in lbl_add: lbl_add.append("ai-reviewed")
        if lbl_add: gh_add_labels(n, lbl_add)

        resp_t  = a.get("response","")
        model_u = alive()[0]["model"] if alive() else "?"

        if resp_t and action in ("respond","close"):
            comment = (
                f"## 🤖 MaxOS AI — Analyse\n\n{resp_t}\n\n"
                f"---\n*Type: `{a.get('type','?')}` | MaxOS AI v{VERSION}*"
            )
            gh_post_comment(n, comment)

        if action == "close":
            gh_close_issue(n, "completed")

        disc_log(f"🎫 Issue #{n}", f"**{title[:45]}** | `{action}`", 0x5865F2)
        treated += 1
        time.sleep(1)

    log(f"Issues: {treated} traitée(s)")
    return ms_cache

def handle_stale(days_stale=21, days_close=7):
    issues = gh_open_issues()
    now    = time.time()
    marked = closed = 0
    for issue in issues:
        n      = issue.get("number")
        upd    = issue.get("updated_at","")
        labels = [l.get("name","") for l in issue.get("labels",[])]
        author = issue.get("user",{}).get("login","")
        if author in BOT_LOGINS: continue
        if any(l in labels for l in ("wontfix","security","bug")): continue
        is_stale = "stale" in labels
        try: upd_ts = datetime.strptime(upd,"%Y-%m-%dT%H:%M:%SZ").timestamp()
        except: continue
        age = now - upd_ts
        if age >= (days_stale+days_close)*86400 and is_stale:
            gh_post_comment(n, f"🤖 **MaxOS AI**: Fermeture après **{int(age/86400)}j** d'inactivité.")
            gh_close_issue(n, "not_planned")
            closed += 1
        elif age >= days_stale*86400 and not is_stale:
            gh_add_labels(n, ["stale"])
            gh_post_comment(n, f"⏰ **MaxOS AI**: Inactive depuis **{int(age/86400)}j**. Fermeture dans {days_close}j.")
            marked += 1
    if marked+closed: log(f"Stale: {marked} marquées, {closed} fermées")

def handle_prs():
    prs = gh_open_prs()
    if not prs: log("PRs: aucune"); return
    log(f"PRs: {len(prs)} ouverte(s)")
    reviewed = 0
    for pr in prs[:5]:
        n      = pr.get("number")
        title  = pr.get("title","")
        author = pr.get("user",{}).get("login","")
        if pr.get("state") != "open": continue
        if author in BOT_LOGINS: continue
        revs = gh_pr_reviews(n)
        if any(r.get("user",{}).get("login","") in BOT_LOGINS for r in (revs or [])): continue
        if not watchdog(): break

        files_d = gh_pr_files(n)
        patches = ""
        for f in files_d[:5]:
            if f.get("filename","").endswith((".c",".h",".asm")):
                p = f.get("patch","")[:1500]
                if p: patches += f"\n--- {f.get('filename','')} ---\n{p}\n"

        prompt = (
            f"Expert code review MaxOS bare metal x86.\n{RULES}\n"
            f"PR #{n}: {title}\nAuteur: {author}\n\nDiff:\n{patches}\n\n"
            'JSON valide:\n{"decision":"APPROVE|REQUEST_CHANGES|COMMENT","summary":"2 phrases",'
            '"problems":[],"positives":[],"bare_metal_violations":[],"merge_safe":false}'
        )

        a = _parse_json_robust(ai_call(prompt, max_tokens=2000, timeout=60, tag=f"pr/{n}"))
        if not a: a = {}

        decision   = a.get("decision","COMMENT")
        merge_safe = a.get("merge_safe",False)
        icon       = {"APPROVE":"✅","REQUEST_CHANGES":"🔴","COMMENT":"💬"}.get(decision,"💬")
        model_u    = alive()[0]["model"] if alive() else "?"

        body = (f"## {icon} Code Review MaxOS AI — PR #{n}\n\n"
                f"{a.get('summary','Analyse non disponible.')}\n\n")
        if a.get("problems"):
            body += "### ❌ Problèmes\n" + "\n".join(f"- {p}" for p in a["problems"][:6]) + "\n\n"
        if a.get("bare_metal_violations"):
            body += "### ⚠️ Violations bare metal\n" + "\n".join(f"- {v}" for v in a["bare_metal_violations"][:5]) + "\n\n"
        if a.get("positives"):
            body += "### ✅ Points positifs\n" + "\n".join(f"- {p}" for p in a["positives"][:5]) + "\n\n"
        body += f"\n---\n*MaxOS AI v{VERSION} | {model_u}*"

        if decision == "APPROVE" and merge_safe:
            gh_approve_pr(n, body)
            gh_add_labels(n, ["ai-approved","ai-reviewed"])
        elif decision == "REQUEST_CHANGES":
            gh_req_changes(n, body)
            gh_add_labels(n, ["ai-rejected","needs-fix","ai-reviewed"])
        else:
            gh_post_review(n, body, "COMMENT")
            gh_add_labels(n, ["ai-reviewed"])

        disc_log(f"📋 PR #{n} — {decision}", f"**{title[:45]}**", 0x00AAFF)
        reviewed += 1
        time.sleep(1)
    log(f"PRs: {reviewed} reviewée(s)")

# ─── RELEASE ──────────────────────────────────────────────────────────────────
def create_release(tasks_done, tasks_failed, analyse, stats):
    releases  = gh_list_releases(10)
    last_tag  = "v0.0.0"
    for r in releases:
        tag = r.get("tag_name","")
        if re.match(r"v\d+\.\d+\.\d+", tag):
            last_tag = tag; break
    try:
        pts = last_tag.lstrip("v").split(".")
        major, minor, patch = int(pts[0]), int(pts[1]), int(pts[2])
    except: major = minor = patch = 0

    score = analyse.get("score_actuel",35)
    if score >= 80:   major += 1; minor = 0; patch = 0
    elif score >= 60: minor += 1; patch = 0
    else:             patch += 1
    new_tag = f"v{major}.{minor}.{patch}"

    # Check if os.img exists
    img_path = os.path.join(REPO_PATH, "os.img")
    img_ok   = os.path.exists(img_path) and os.path.getsize(img_path) > 0
    img_size = os.path.getsize(img_path) if img_ok else 0

    compare   = gh_compare(last_tag, "HEAD")
    commits   = compare.get("commits",[])
    ahead_by  = compare.get("ahead_by", len(commits))
    chg_lines = []
    for c in commits[:20]:
        sha = c.get("sha","")[:7]
        msg = c.get("commit",{}).get("message","").split("\n")[0][:80]
        if msg and not msg.startswith("[skip"): chg_lines.append(f"- `{sha}` {msg}")
    changelog = "\n".join(chg_lines) or "- Maintenance"

    changes_ok = "".join(
        f"- ✅ **{t.get('nom','?')[:50]}** [`{t.get('sha','?')[:7]}`]"
        f"{' (fix×'+str(t['fix_count'])+')' if t.get('fix_count',0)>0 else ''}"
        f" — {t.get('elapsed',0):.0f}s\n"
        for t in tasks_done
    )
    changes_fail = ("\n## ⏭️ Reporté\n\n" + "\n".join(f"- ❌ {n}" for n in tasks_failed) + "\n") if tasks_failed else ""

    tk    = sum(p["tokens"] for p in PROVIDERS)
    calls = sum(p["calls"]  for p in PROVIDERS)
    now   = datetime.utcnow()

    prov_table = ""
    for p in sorted(PROVIDERS, key=lambda x: -x["calls"]):
        if p["calls"] == 0: continue
        st = "💀" if p["dead"] else "🟢"
        prov_table += f"| {st} `{p['id']}` | {p['calls']} | ~{p['tokens']:,} | {avg_rt(p):.1f}s |\n"

    body = (
        f"# 🖥️ MaxOS {new_tag}\n\n"
        f"> 🤖 Généré par **MaxOS AI v{VERSION}**\n\n---\n\n"
        f"## 📊 État\n\n| Métrique | Valeur |\n|---|---|\n"
        f"| 🎯 Score | **{score}/100** |\n"
        f"| 📈 Niveau | {analyse.get('niveau_os','?')} |\n"
        f"| 📁 Fichiers | {stats.get('files',0)} |\n"
        f"| 📝 Lignes | {stats.get('lines',0):,} |\n"
        f"| 💾 os.img | {'✅ '+str(img_size)+' bytes' if img_ok else '❌ non généré'} |\n\n"
        f"## ✅ Améliorations ({len(tasks_done)})\n\n{changes_ok or '*(aucune)*'}"
        f"{changes_fail}\n"
        f"## 📝 Changelog {last_tag} → {new_tag} ({ahead_by} commits)\n\n{changelog}\n\n"
        f"## 🚀 Tester\n\n```bash\n"
        f"qemu-system-i386 -drive format=raw,file=os.img,if=floppy -boot a -vga std -k fr -m 32\n"
        f"```\n\n"
        f"## 🤖 Stats IA\n\n| Métrique | Valeur |\n|---|---|\n"
        f"| Appels IA | {_CYCLE_STATS.get('ai_calls',0)} |\n"
        f"| 429 total | {_CYCLE_STATS.get('total_429',0)} |\n"
        f"| Tokens | ~{tk:,} |\n"
        f"| Builds OK | {_CYCLE_STATS.get('builds_ok',0)} |\n"
        f"| Auto-fix OK | {_CYCLE_STATS.get('auto_fix_success',0)} |\n\n"
        f"### Providers\n\n| Status | ID | Appels | Tokens | Avg RT |\n|---|---|---|---|---|\n"
        f"{prov_table or '*(aucun)*'}\n\n"
        f"---\n*MaxOS AI v{VERSION} | {now.strftime('%Y-%m-%d %H:%M')} UTC*\n"
    )

    pre = score < 50
    url = gh_create_release(new_tag,
                             f"MaxOS {new_tag} — {analyse.get('niveau_os','?')} — {now.strftime('%Y-%m-%d')}",
                             body, pre=pre)
    if url:
        disc_now(
            f"🚀 Release {new_tag} !",
            f"Score: **{score}/100** | os.img: {'✅' if img_ok else '❌'}",
            0x00FF88 if not pre else 0xFFA500,
            [{"name":"🏷️ Version","value":new_tag,"inline":True},
             {"name":"📊 Score","value":f"{score}/100","inline":True},
             {"name":"💾 os.img","value":"✅ Bootable" if img_ok else "❌ Manquant","inline":True},
             {"name":"🔗 Lien","value":f"[Release]({url})","inline":False}]
        )
        log(f"Release {new_tag}: {url}", "OK")
    else:
        log("Release: échec", "ERROR")
    return url

def final_report(success, total, tasks_done, tasks_failed, analyse, stats):
    score   = analyse.get("score_actuel",35)
    pct     = int(success/total*100) if total > 0 else 0
    color   = 0x00FF88 if pct >= 80 else 0xFFA500 if pct >= 50 else 0xFF4444
    elapsed = int(time.time() - START_TIME)
    tk      = sum(p["tokens"] for p in PROVIDERS)
    calls   = sum(p["calls"]  for p in PROVIDERS)
    img_ok  = os.path.exists(os.path.join(REPO_PATH,"os.img"))
    sources  = read_all()
    qual     = analyze_quality(sources)

    done_s = "\n".join(
        f"✅ {t.get('nom','?')[:42]} ({t.get('elapsed',0):.0f}s)"
        + (f" fix×{t['fix_count']}" if t.get("fix_count",0)>0 else "")
        for t in tasks_done
    ) or "Aucune"
    fail_s = "\n".join(f"❌ {n[:42]}" for n in tasks_failed) or "Aucune"

    disc_now(
        f"🏁 Cycle terminé — {success}/{total}",
        f"```\n{pbar(pct)}\n```\n**{pct}% réussite** | os.img: {'✅' if img_ok else '❌'}",
        color,
        [
            {"name":"✅ Succès","value":str(success),"inline":True},
            {"name":"❌ Échecs","value":str(total-success),"inline":True},
            {"name":"📈 Taux","value":f"{pct}%","inline":True},
            {"name":"⏱️ Durée","value":f"{elapsed}s ({uptime()})","inline":True},
            {"name":"🔑 Appels","value":str(calls),"inline":True},
            {"name":"💬 Tokens","value":f"{tk:,}","inline":True},
            {"name":"📊 Qualité","value":f"{qual['score']}/100","inline":True},
            {"name":"💾 os.img","value":"✅ OK" if img_ok else "❌ Manquant","inline":True},
            {"name":"🏆 Score OS","value":f"{score}/100","inline":False},
            {"name":"✅ Réussies","value":done_s[:900],"inline":False},
            {"name":"❌ Échouées","value":fail_s[:500],"inline":False},
            {"name":"🔑 Providers","value":prov_summary()[:600],"inline":False},
        ]
    )

# ─── MAIN ────────────────────────────────────────────────────────────────────
def main():
    print("=" * 64)
    print(f"  MaxOS AI Developer v{VERSION}")
    print(f"  Ultra-robuste | Multi-provider | Bare metal x86")
    print("=" * 64)

    if not PROVIDERS:
        print("FATAL: Aucun provider IA configuré.")
        sys.exit(1)

    by_type = defaultdict(list)
    for p in PROVIDERS: by_type[p["type"]].append(p)
    for t in sorted(by_type.keys()):
        ps = by_type[t]
        ku = len(set(p["key"][:8] for p in ps))
        mu = len(set(p["model"] for p in ps))
        print(f"  {t:12s}: {ku} clé(s) × {mu} modèle(s) = {len(ps)} providers")
    print(f"  {'TOTAL':12s}: {len(PROVIDERS)} providers")
    print(f"  {'RUNTIME':12s}: {MAX_RUNTIME}s max | DEBUG: {'ON' if DEBUG else 'OFF'}")
    print("=" * 64 + "\n")

    disc_now(
        f"🤖 MaxOS AI v{VERSION} — Démarrage",
        f"`{len(PROVIDERS)}` providers IA",
        0x5865F2,
        [{"name":"🔑 Providers","value":prov_summary()[:800],"inline":False},
         {"name":"📁 Repo","value":f"`{REPO_OWNER}/{REPO_NAME}`","inline":True},
         {"name":"⏱️ Runtime","value":f"{MAX_RUNTIME}s max","inline":True}]
    )

    subprocess.run(["make","clean"], cwd=REPO_PATH, capture_output=True, timeout=30)

    log("Setup: labels GitHub...")
    gh_ensure_labels(STANDARD_LABELS)

    ms_cache = {}

    # Issues & PRs — time-boxed
    log("[Issues] Traitement...")
    ms_cache = handle_issues(ms_cache) or ms_cache
    if not watchdog(): sys.exit(0)

    log("[Stale] Vérification...")
    handle_stale(days_stale=21, days_close=7)
    if not watchdog(): sys.exit(0)

    log("[PRs] Traitement...")
    handle_prs()
    if not watchdog(): sys.exit(0)

    log("[Pre-flight] Build initial...")
    pf_ok, pf_errs = pre_flight_check()
    if not pf_ok:
        log(f"Build pré-existant cassé: {len(pf_errs)} err", "WARN")

    sources = read_all(force=True)
    stats   = proj_stats(sources)
    qual    = analyze_quality(sources)

    log(f"Sources: {stats['files']} fichiers | {stats['lines']:,} lignes")
    log(f"Qualité: {qual['score']}/100 | {len(qual['violations'])} violation(s)")

    disc_now("📊 Sources",
             f"`{stats['files']}` fichiers | `{stats['lines']:,}` lignes",
             0x5865F2,
             [{"name":"Qualité","value":f"{qual['score']}/100","inline":True},
              {"name":"Fichiers C","value":f"{qual['c_files']} .c/.h","inline":True},
              {"name":"ASM","value":f"{qual['asm_files']} .asm","inline":True}])

    analyse   = phase_analyse(build_ctx(sources), stats)
    score     = analyse.get("score_actuel",35)
    niveau    = analyse.get("niveau_os","?")
    plan      = analyse.get("plan_ameliorations",[])
    milestone = analyse.get("prochaine_milestone","?")
    features  = analyse.get("fonctionnalites_presentes",[])
    manques   = analyse.get("fonctionnalites_manquantes_critiques",[])

    order = {"CRITIQUE":0,"HAUTE":1,"NORMALE":2,"BASSE":3,"ELEVEE":1}
    plan  = sorted(plan, key=lambda t: (order.get(t.get("priorite","NORMALE"),2), t.get("nom","")))

    log(f"Score={score}/100 | {niveau} | {len(plan)} tâche(s)", "STAT")

    if milestone and milestone not in ms_cache:
        ms_num = gh_ensure_milestone(milestone, f"Objectif: {milestone}")
        if ms_num: ms_cache[milestone] = ms_num

    disc_now(
        f"📊 Analyse: {score}/100",
        f"```\n{pbar(score)}\n```",
        0x00AAFF if score >= 60 else 0xFFA500 if score >= 30 else 0xFF4444,
        [{"name":"✅ Présentes","value":"\n".join(f"+ {f}" for f in features[:6]) or "—","inline":True},
         {"name":"❌ Manquantes","value":"\n".join(f"- {f}" for f in manques[:6]) or "—","inline":True},
         {"name":"📋 Plan",
          "value":"\n".join(f"[{i+1}] `{t.get('priorite','?')[:3]}` {t.get('nom','?')[:38]}"
                            for i, t in enumerate(plan[:8])) or "—","inline":False},
         {"name":"🎯 Milestone","value":milestone[:80],"inline":True}]
    )

    total        = len(plan)
    success      = 0
    tasks_done   = []
    tasks_failed = []

    for i, task in enumerate(plan, 1):
        if not watchdog():
            log(f"Watchdog: arrêt avant tâche {i}/{total}", "WARN")
            break
        if remaining_time() < 200:
            log(f"Moins de 200s restantes — arrêt avant tâche {i}/{total}", "WARN")
            break

        disc_log(
            f"💓 [{i}/{total}] {task.get('nom','?')[:45]}",
            f"Uptime: {uptime()} | Reste: {int(remaining_time())}s\n{prov_summary()[:250]}",
            0x7289DA
        )

        sources_now = read_all()
        ok, written, deleted, metrics = implement(task, sources_now, i, total)
        TASK_METRICS.append(metrics)

        if ok:
            success += 1
            tasks_done.append(metrics)
        else:
            tasks_failed.append(task.get("nom","?"))

        if i < total and watchdog():
            n_al  = len(alive())
            pause = 3 if n_al >= 5 else 6 if n_al >= 3 else 12 if n_al >= 1 else 20
            log(f"Pause {pause}s ({n_al} dispo, {int(remaining_time())}s restants)")
            _flush_disc(True)
            time.sleep(pause)

    log(f"\n{'='*56}\nCYCLE TERMINÉ: {success}/{total}\n{'='*56}")

    sf = read_all(force=True)
    if success > 0:
        log("[Release] Création...")
        create_release(tasks_done, tasks_failed, analyse, proj_stats(sf))
    else:
        log("[Release] 0 succès — pas de release")

    final_report(success, total, tasks_done, tasks_failed, analyse, proj_stats(sf))
    _flush_disc(True)

    print(f"\n{'='*64}")
    print(f"[FIN] {success}/{total} | uptime: {uptime()} | GH RL: {GH_RATE['remaining']}")
    img_ok = os.path.exists(os.path.join(REPO_PATH,"os.img"))
    print(f"      os.img: {'✅ OK' if img_ok else '❌ MANQUANT'}")
    print(f"      IA calls: {_CYCLE_STATS.get('ai_calls',0)} | 429: {_CYCLE_STATS.get('total_429',0)}")
    for t in tasks_done:
        fc = t.get("fix_count",0)
        print(f"  ✅ {t.get('nom','?')[:58]} ({t.get('elapsed',0):.0f}s){' fix×'+str(fc) if fc else ''}")
    for n in tasks_failed:
        print(f"  ❌ {n[:58]}")
    print("=" * 64)

if __name__ == "__main__":
    main()
