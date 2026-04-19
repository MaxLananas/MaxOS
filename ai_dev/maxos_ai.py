#!/usr/bin/env python3

import os, sys, json, time, subprocess, re, hashlib, traceback, random, socket, atexit
import urllib.request, urllib.error, urllib.parse
from datetime import datetime, timezone
from collections import defaultdict, deque

VERSION     = "15.1"
DEBUG       = os.environ.get("MAXOS_DEBUG", "0") == "1"
START_TIME  = time.time()
MAX_RUNTIME = 3300

REPO_OWNER  = os.environ.get("REPO_OWNER", "MaxLananas")
REPO_NAME   = os.environ.get("REPO_NAME",  "MaxOS")
REPO_PATH   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GH_TOKEN    = os.environ.get("GH_PAT", "") or os.environ.get("GITHUB_TOKEN", "")
DISCORD_WH  = os.environ.get("DISCORD_WEBHOOK", "")

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash-lite-preview-06-17",
    "gemini-2.0-flash",
]

OPENROUTER_MODELS = [
    "google/gemini-2.5-flash-preview:free",
    "qwen/qwen-2.5-coder-32b-instruct:free",
    "deepseek/deepseek-r1-distill-llama-70b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "microsoft/phi-4-reasoning:free",
    "deepseek/deepseek-r1:free",
    "google/gemini-2.0-flash-exp:free",
    "mistralai/mistral-small-3.2-24b-instruct:free",
    "nvidia/llama-3.1-nemotron-ultra-253b-v1:free",
]

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "meta-llama/llama-4-scout-17b-16e-instruct",
    "qwen/qwen3-32b",
]

MISTRAL_MODELS = [
    "mistral-small-latest",
    "open-mixtral-8x7b",
    "mistral-medium-latest",
]

def _find_keys(prefix):
    keys = []
    for suffix in [""] + [f"_{i}" for i in range(2, 12)]:
        v = os.environ.get(f"{prefix}{suffix}", "").strip()
        if len(v) >= 8:
            keys.append(v)
    return keys

def _make_provider(ptype, pid, key, model, url):
    return {
        "type":           ptype,
        "id":             pid,
        "key":            key,
        "model":          model,
        "url":            url,
        "cooldown":       0.0,
        "errors":         0,
        "calls":          0,
        "tokens":         0,
        "dead":           False,
        "last_ok":        0.0,
        "response_times": deque(maxlen=10),
        "consec_429":     0,
        "success_rate":   1.0,
    }

def load_providers():
    pools = []

    gem_keys = _find_keys("GEMINI_API_KEY")
    print(f"  [load] GEMINI     : {len(gem_keys)} clé(s) × {len(GEMINI_MODELS)} modèles = {len(gem_keys)*len(GEMINI_MODELS)}")
    gem = []
    for i, key in enumerate(gem_keys, 1):
        for m in GEMINI_MODELS:
            base = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
            slug = m.replace("gemini-", "").replace("-", "").replace(".", "")[:14]
            pid  = f"gm{i}_{slug}"
            gem.append(_make_provider("gemini", pid, key, m, f"{base}?key={key}"))
    if gem:
        pools.append(gem)

    or_keys = _find_keys("OPENROUTER_KEY")
    print(f"  [load] OPENROUTER : {len(or_keys)} clé(s) × {len(OPENROUTER_MODELS)} modèles = {len(or_keys)*len(OPENROUTER_MODELS)}")
    orl = []
    for i, key in enumerate(or_keys, 1):
        for m in OPENROUTER_MODELS:
            short = m.split("/")[-1].replace(":free", "")[:16]
            orl.append(_make_provider("openrouter", f"or{i}_{short}", key, m,
                                      "https://openrouter.ai/api/v1/chat/completions"))
    if orl:
        pools.append(orl)

    groq_keys = _find_keys("GROQ_KEY")
    print(f"  [load] GROQ       : {len(groq_keys)} clé(s) × {len(GROQ_MODELS)} modèles = {len(groq_keys)*len(GROQ_MODELS)}")
    gro = []
    for i, key in enumerate(groq_keys, 1):
        for m in GROQ_MODELS:
            slug = m.replace("/", "_").replace("-", "_")[:16]
            gro.append(_make_provider("groq", f"gr{i}_{slug}", key, m,
                                      "https://api.groq.com/openai/v1/chat/completions"))
    if gro:
        pools.append(gro)

    mis_keys = _find_keys("MISTRAL_KEY")
    print(f"  [load] MISTRAL    : {len(mis_keys)} clé(s) × {len(MISTRAL_MODELS)} modèles = {len(mis_keys)*len(MISTRAL_MODELS)}")
    mis = []
    for i, key in enumerate(mis_keys, 1):
        for m in MISTRAL_MODELS:
            mis.append(_make_provider("mistral", f"ms{i}_{m[:16]}", key, m,
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

PROVIDERS    = load_providers()
_RR          = 0
GH_RATE      = {"remaining": 5000, "reset": 0}
SOURCE_CACHE = {"hash": None, "data": None}
TASK_METRICS = []
_DISC_BUF    = []
_DISC_LAST   = 0.0
_DISC_INTV   = 10
_CYCLE_STATS = defaultdict(int)

def ts():
    return datetime.now(timezone.utc).strftime("%H:%M:%S")

def uptime():
    s       = int(time.time() - START_TIME)
    h, r    = divmod(s, 3600)
    m, s    = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def pbar(pct, w=20):
    pct = max(0, min(100, pct))
    f   = int(w * pct / 100)
    return "█" * f + "░" * (w - f) + f" {pct}%"

ICONS = {
    "INFO":  "📋",
    "WARN":  "⚠️ ",
    "ERROR": "❌",
    "OK":    "✅",
    "BUILD": "🔨",
    "GIT":   "📦",
    "TIME":  "⏱️ ",
    "AI":    "🤖",
    "STAT":  "📊",
}

def log(msg, level="INFO"):
    print(f"[{ts()}] {ICONS.get(level, '📋')} {msg}", flush=True)

def watchdog():
    elapsed = time.time() - START_TIME
    if elapsed >= MAX_RUNTIME:
        log(f"Watchdog déclenché: {int(elapsed)}s/{MAX_RUNTIME}s | {uptime()}", "WARN")
        disc_now("⏰ Watchdog", f"Arrêt automatique après **{uptime()}**\nRuntime: {int(elapsed)}s", 0xFFA500)
        return False
    return True

def remaining_time():
    return max(0, MAX_RUNTIME - (time.time() - START_TIME))

def alive():
    now = time.time()
    available = [p for p in PROVIDERS if not p["dead"] and now >= p["cooldown"]]
    available.sort(key=lambda p: (p["consec_429"] * 10 + p["errors"], p["cooldown"]))
    return available

def non_dead():
    return [p for p in PROVIDERS if not p["dead"]]

def prov_summary():
    now = time.time()
    by  = defaultdict(lambda: [0, 0, 0])
    for p in PROVIDERS:
        t = p["type"]
        if p["dead"]:
            by[t][2] += 1
        elif now >= p["cooldown"]:
            by[t][0] += 1
        else:
            by[t][1] += 1
    parts = []
    for t in sorted(by.keys()):
        v = by[t]
        parts.append(f"**{t}**: 🟢{v[0]} 🟡{v[1]} 💀{v[2]}")
    al = len(alive())
    nd = len(non_dead())
    return f"{al}/{nd} dispo — " + " | ".join(parts)

def avg_rt(p):
    rt = p.get("response_times", [])
    if not rt:
        return 999.0
    return sum(rt) / len(rt)

def penalize(p, secs=None, dead=False):
    if dead:
        p["dead"] = True
        _CYCLE_STATS["providers_dead"] += 1
        log(f"Provider {p['id']} ({p['type']}/{p['model']}) → MORT", "ERROR")
        return
    p["errors"]      += 1
    p["consec_429"]  += 1
    p["success_rate"] = max(0.0, p["success_rate"] - 0.15)
    if secs is None:
        base = 15 * (2 ** min(p["errors"] - 1, 4))
        jitter = random.uniform(0, 3)
        secs   = min(base + jitter, 180)
    p["cooldown"] = time.time() + secs
    log(f"Provider {p['id']} → cooldown {int(secs)}s (errs={p['errors']} consec429={p['consec_429']})", "WARN")

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
        _RR = (_RR + 1) % len(al)
        chosen = al[_RR]
        if DEBUG:
            log(f"  pick → {chosen['id']} (avg_rt={avg_rt(chosen):.1f}s sr={chosen['success_rate']:.2f})", "INFO")
        return chosen
    nd = non_dead()
    if not nd:
        log("FATAL: tous les providers sont morts — arrêt immédiat", "ERROR")
        disc_now("💀 Mort totale", "Aucun provider disponible.\nArrêt forcé.", 0xFF0000)
        sys.exit(1)
    best = min(nd, key=lambda p: p["cooldown"])
    wait = max(best["cooldown"] - time.time() + 0.5, 0.5)
    wait = min(wait, 90)
    log(f"Tous en cooldown → attente {int(wait)}s → {best['id']} ({best['type']})", "TIME")
    _CYCLE_STATS["total_waits"] += 1
    _CYCLE_STATS["total_wait_secs"] += int(wait)
    disc_log("⏳ Cooldown global", f"Attente **{int(wait)}s** → `{best['id']}`\n{prov_summary()}", 0xFF8800)
    time.sleep(wait)
    return best

def _call_gemini(p, prompt, max_tok, timeout):
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tok,
            "temperature":     0.05,
            "candidateCount":  1,
        },
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
    if finish in ("SAFETY", "RECITATION", "PROHIBITED_CONTENT"):
        log(f"Gemini bloqué: finishReason={finish}", "WARN")
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
        max_tok = min(max_tok, 8000)
        if len(prompt) > 26000:
            prompt = prompt[:26000] + "\n[TRONQUÉ — CONTINUER LE CODE]"
    elif p["type"] == "openrouter":
        if len(prompt) > 45000:
            prompt = prompt[:45000] + "\n[TRONQUÉ]"

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
        headers["X-Title"]      = f"MaxOS AI Developer v{VERSION}"

    req = urllib.request.Request(p["url"], data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode("utf-8"))

    if "error" in data:
        msg = data["error"].get("message", "unknown error")[:250]
        raise RuntimeError(f"API error: {msg}")

    choices = data.get("choices", [])
    if not choices:
        return None
    content = choices[0].get("message", {}).get("content", "")
    return content.strip() if content else None

def ai_call(prompt, max_tokens=32768, timeout=160, tag="?"):
    if len(prompt) > 54000:
        prompt = prompt[:54000] + "\n[TRONQUÉ]"

    max_att    = min(len(PROVIDERS) * 2, 40)
    last_error = "aucune tentative"
    _CYCLE_STATS["ai_calls"] += 1

    for attempt in range(1, max_att + 1):
        if not watchdog():
            return None
        p  = pick()
        t0 = time.time()
        log(f"[{tag}] {p['type']}/{p['id']} att={attempt}/{max_att} sr={p['success_rate']:.2f}", "AI")

        try:
            if p["type"] == "gemini":
                text = _call_gemini(p, prompt, max_tokens, timeout)
            else:
                text = _call_compat(p, prompt, max_tokens, timeout)

            elapsed = round(time.time() - t0, 1)

            if not text or not text.strip():
                log(f"[{tag}] Réponse vide ({p['id']}) en {elapsed}s", "WARN")
                penalize(p, 12)
                continue

            est_tk       = len(text) // 4
            p["calls"]  += 1
            p["tokens"] += est_tk
            reward(p, elapsed)
            _CYCLE_STATS["total_tokens"] += est_tk
            log(f"[{tag}] ✅ {len(text):,}c {elapsed}s ~{est_tk}tk ({p['type']}/{p['model'][:22]})", "OK")
            return text

        except urllib.error.HTTPError as e:
            elapsed = round(time.time() - t0, 1)
            body    = ""
            try:
                body = e.read().decode("utf-8", errors="replace")[:600]
            except Exception:
                pass
            last_error = f"HTTP {e.code}"
            log(f"[{tag}] HTTP {e.code} ({p['id']}) {elapsed}s", "WARN")
            if DEBUG:
                log(f"  ↳ body: {body[:300]}", "WARN")

            if e.code == 429:
                _CYCLE_STATS["total_429"] += 1
                penalize(p)
                al_now = [x for x in alive() if x is not p]
                if not al_now:
                    nd_local = non_dead()
                    if nd_local:
                        nxt  = min(x["cooldown"] for x in nd_local) - time.time()
                        wait = max(min(nxt + 0.5, 30), 1)
                    else:
                        wait = 30
                    log(f"[{tag}] Rien dispo → attente {int(wait)}s", "TIME")
                    time.sleep(wait)

            elif e.code == 403:
                bl = body.lower()
                kill_words = ["denied", "banned", "suspended", "not authorized",
                              "no access", "forbidden", "deactivated", "invalid api key"]
                if any(w in bl for w in kill_words):
                    penalize(p, dead=True)
                else:
                    penalize(p, 180)

            elif e.code == 404:
                penalize(p, dead=True)

            elif e.code == 400:
                if DEBUG:
                    log(f"  ↳ 400 body: {body[:200]}", "WARN")
                penalize(p, 40)

            elif e.code == 401:
                penalize(p, dead=True)

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
            last_error = f"timeout {timeout}s"
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
            log(f"[{tag}] JSONDecodeError ({p['id']}): {e}", "WARN")
            last_error = f"json decode: {e}"
            penalize(p, 10)

        except Exception as e:
            log(f"[{tag}] Exception ({p['id']}): {type(e).__name__}: {e}", "ERROR")
            last_error = f"{type(e).__name__}: {str(e)[:80]}"
            if DEBUG:
                traceback.print_exc()
            penalize(p, 12)
            time.sleep(1)

    _CYCLE_STATS["ai_failures"] += 1
    log(f"[{tag}] ÉCHEC TOTAL {max_att} att. Dernière err: {last_error}", "ERROR")
    return None

def _disc_raw(embeds):
    if not DISCORD_WH:
        return False
    payload = json.dumps({
        "username":   f"MaxOS AI v{VERSION}",
        "avatar_url": "https://raw.githubusercontent.com/MaxLananas/MaxOS/main/ai_dev/avatar.png",
        "embeds":     embeds[:10],
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
        if DEBUG:
            log(f"Discord err: {ex}", "WARN")
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
        "footer":      {
            "text": (
                f"v{VERSION} | {cur} | {al}/{nd} prov | "
                f"up {uptime()} | ~{tk:,}tk | {ca}c | GH:{GH_RATE['remaining']}"
            )
        },
    }
    if fields:
        e["fields"] = [
            {
                "name":   str(f.get("name", "?"))[:256],
                "value":  str(f.get("value", "?"))[:1024],
                "inline": bool(f.get("inline", False)),
            }
            for f in fields[:25]
            if f.get("value") and str(f.get("value", "")).strip()
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
        embeds.append(_make_embed(t, d, c))
    if embeds:
        _disc_raw(embeds)
        _DISC_LAST = time.time()

def disc_now(title, desc="", color=0x5865F2, fields=None):
    _flush_disc(True)
    _disc_raw([_make_embed(title, desc, color, fields)])

atexit.register(_flush_disc, True)

def gh_api(method, endpoint, data=None, raw_url=None, retry=3, silent=False):
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
                if GH_RATE["remaining"] < 80:
                    log(f"GH rate limit critique: {GH_RATE['remaining']} restants !", "WARN")
                raw  = r.read().decode("utf-8", errors="replace")
                return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", errors="replace")[:400]
            except Exception:
                pass
            if e.code == 403 and "rate limit" in body.lower():
                wait = max(GH_RATE["reset"] - time.time() + 5, 60)
                log(f"GH rate limit 403 → attente {int(wait)}s", "WARN")
                time.sleep(wait)
                continue
            if e.code in (500, 502, 503, 504) and att < retry:
                time.sleep(5 * att)
                continue
            if not silent:
                log(f"GH {method} {endpoint[:60]} HTTP {e.code}: {body[:120]}", "WARN")
            return None
        except Exception as ex:
            if att < retry:
                time.sleep(3)
                continue
            if not silent:
                log(f"GH ex: {type(ex).__name__}: {ex}", "ERROR")
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
            {"path": c["path"], "line": c.get("line", 1), "side": "RIGHT", "body": c["body"]}
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
        "commit_title": f"merge: {title[:60]} [AI]",
        "merge_method": "squash",
    })
    return bool(r and r.get("merged"))

def gh_open_issues():
    r = gh_api("GET", "issues?state=open&per_page=30&sort=updated&direction=desc")
    if not isinstance(r, list):
        return []
    return [i for i in r if not i.get("pull_request")]

def gh_issue_comments(n):
    r = gh_api("GET", f"issues/{n}/comments?per_page=50")
    return r if isinstance(r, list) else []

def gh_issue_timeline(n):
    r = gh_api("GET", f"issues/{n}/timeline?per_page=50",
               raw_url=f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{n}/timeline?per_page=50")
    return r if isinstance(r, list) else []

def gh_close_issue(n, reason="completed"):
    gh_api("PATCH", f"issues/{n}", {"state": "closed", "state_reason": reason})

def gh_add_labels(n, labels):
    if labels:
        gh_api("POST", f"issues/{n}/labels", {"labels": labels})

def gh_post_comment(n, body):
    gh_api("POST", f"issues/{n}/comments", {"body": body})

def gh_update_issue(n, data):
    gh_api("PATCH", f"issues/{n}", data)

def gh_create_issue(title, body, labels=None, milestone=None):
    pay = {"title": title, "body": body}
    if labels:
        pay["labels"] = labels
    if milestone:
        pay["milestone"] = milestone
    return gh_api("POST", "issues", pay)

def gh_list_labels():
    r = gh_api("GET", "labels?per_page=100")
    return {l["name"]: l for l in (r if isinstance(r, list) else [])}

def gh_ensure_labels(desired):
    ex = gh_list_labels()
    created = 0
    for name, color in desired.items():
        if name not in ex:
            gh_api("POST", "labels", {
                "name":        name,
                "color":       color,
                "description": f"[MaxOS AI] {name}",
            })
            created += 1
    if created:
        log(f"Labels: {created} créé(s)")

STANDARD_LABELS = {
    "ai-reviewed":  "0075ca",
    "ai-approved":  "0e8a16",
    "ai-rejected":  "b60205",
    "ai-generated": "8b5cf6",
    "needs-fix":    "e4e669",
    "needs-review": "fbca04",
    "bug":          "d73a4a",
    "enhancement":  "a2eeef",
    "question":     "d876e3",
    "stale":        "eeeeee",
    "wontfix":      "ffffff",
    "invalid":      "e4e4e4",
    "duplicate":    "cfd3d7",
    "kernel":       "5319e7",
    "driver":       "1d76db",
    "app":          "0052cc",
    "boot":         "e11d48",
    "performance":  "f9d0c4",
    "security":     "b91c1c",
    "documentation":"0ea5e9",
    "good-first-issue": "7057ff",
}

def gh_ensure_milestone(title, description=""):
    r = gh_api("GET", "milestones?state=open&per_page=30")
    for m in (r if isinstance(r, list) else []):
        if m.get("title") == title:
            return m.get("number")
    r2 = gh_api("POST", "milestones", {
        "title":       title,
        "description": description or f"[AI] {title}",
    })
    return r2.get("number") if r2 else None

def gh_assign_ms(issue_num, ms_num):
    if ms_num:
        gh_api("PATCH", f"issues/{issue_num}", {"milestone": ms_num})

def gh_list_releases(n=10):
    r = gh_api("GET", f"releases?per_page={n}")
    return r if isinstance(r, list) else []

def gh_create_release(tag, name, body, pre=False):
    r = gh_api("POST", "releases", {
        "tag_name":         tag,
        "target_commitish": "main",
        "name":             name,
        "body":             body,
        "draft":            False,
        "prerelease":       pre,
    })
    return r.get("html_url") if r and "html_url" in r else None

def gh_repo_info():
    repo   = gh_api("GET", "") or {}
    langs  = gh_api("GET", "languages") or {}
    pulse  = gh_api("GET", "commits?per_page=1") or []
    return {
        "stars":        repo.get("stargazers_count", 0),
        "forks":        repo.get("forks_count", 0),
        "watchers":     repo.get("subscribers_count", 0),
        "open_issues":  repo.get("open_issues_count", 0),
        "languages":    langs,
        "default_branch": repo.get("default_branch", "main"),
        "size_kb":      repo.get("size", 0),
    }

def gh_compare(base, head):
    r = gh_api("GET", f"compare/{base}...{head}")
    return r if isinstance(r, dict) else {}

def gh_get_workflow_runs(limit=5):
    r = gh_api("GET", f"actions/runs?per_page={limit}&status=success")
    return (r or {}).get("workflow_runs", [])

def git_cmd(args, timeout=60):
    try:
        r = subprocess.run(
            ["git"] + args,
            cwd=REPO_PATH,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return r.returncode == 0, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"git timeout {timeout}s"
    except Exception as e:
        return False, "", str(e)

def git_sha(short=True):
    ok, out, _ = git_cmd(["rev-parse", "HEAD"])
    if not ok:
        return ""
    s = out.strip()
    return s[:7] if short else s

def git_current_branch():
    ok, out, _ = git_cmd(["branch", "--show-current"])
    return out.strip() if ok else "main"

def git_push(task_name, files, desc, model):
    if not files:
        return True, None, None

    dirs   = set(f.split("/")[0] for f in files if "/" in f)
    pmap   = {
        "kernel":  "kernel",
        "drivers": "driver",
        "boot":    "boot",
        "ui":      "ui",
        "apps":    "feat",
    }
    prefix = next((pmap[d] for d in pmap if d in dirs), "feat")
    fshort = ", ".join(os.path.basename(f) for f in files[:3])
    if len(files) > 3:
        fshort += f" +{len(files)-3}"
    short  = f"{prefix}: {task_name[:50]} [{fshort}]"
    body   = (
        f"{short}\n\n"
        f"Files: {', '.join(files[:10])}\n"
        f"Model: {model}\n"
        f"Arch: x86-32 bare metal\n\n"
        f"[skip ci]"
    )

    git_cmd(["add", "-A"])
    ok, out, err = git_cmd(["commit", "-m", body])
    if not ok:
        if "nothing to commit" in (out + err):
            log("Git: rien à committer — déjà à jour")
            return True, None, None
        log(f"Commit KO: {err[:250]}", "ERROR")
        return False, None, None

    sha = git_sha()

    ok2, _, e2 = git_cmd(["push", "--set-upstream", "origin", git_current_branch()])
    if not ok2:
        git_cmd(["pull", "--rebase", "--autostash"])
        ok2, _, e2 = git_cmd(["push"])
        if not ok2:
            log(f"Push KO: {e2[:250]}", "ERROR")
            return False, None, None

    _CYCLE_STATS["total_commits"] += 1
    log(f"Push OK: {sha} — {short[:60]}", "GIT")
    return True, sha, short

_ERR_RE = re.compile(
    r"(?:"
    r"error:"
    r"|fatal error:"
    r"|fatal:"
    r"|undefined reference"
    r"|cannot find"
    r"|no such file"
    r"|\*\*\* \["
    r"|Error \d+\s*$"
    r"|FAILED\s*$"
    r"|nasm:.*error"
    r"|ld:.*error"
    r"|collect2: error"
    r"|linker command failed"
    r"|multiple definition"
    r"|duplicate symbol"
    r"|identifier expected"
    r"|expression syntax"
    r"|undefined symbol"
    r"|cannot open"
    r")",
    re.IGNORECASE
)

def parse_errs(log_text):
    seen = set()
    result = []
    for line in log_text.split("\n"):
        s = line.strip()
        if s and _ERR_RE.search(s) and s not in seen:
            seen.add(s)
            result.append(s[:140])
    return result[:35]

def make_build():
    subprocess.run(
        ["make", "clean"],
        cwd=REPO_PATH, capture_output=True, timeout=30
    )
    t0 = time.time()
    try:
        r = subprocess.run(
            ["make", "-j2"],
            cwd=REPO_PATH,
            capture_output=True,
            text=True,
            timeout=150,
        )
    except subprocess.TimeoutExpired:
        log("Build TIMEOUT 150s", "ERROR")
        return False, "TIMEOUT", ["Build timeout après 150s"]

    el   = round(time.time() - t0, 1)
    ok   = r.returncode == 0
    lt   = r.stdout + r.stderr
    errs = parse_errs(lt)

    log(f"Build {'OK' if ok else f'FAIL ({len(errs)} err)'} {el}s", "BUILD")
    for e in errs[:6]:
        log(f"  >> {e[:115]}", "BUILD")

    if ok:
        _CYCLE_STATS["builds_ok"] += 1
        disc_log("🔨 Build ✅", f"Compilé en `{el}s`", 0x00CC44)
    else:
        _CYCLE_STATS["builds_fail"] += 1
        es = "\n".join(f"`{e[:85]}`" for e in errs[:5])
        disc_log(f"🔨 Build ❌ ({len(errs)} err)", f"`{el}s`\n{es}", 0xFF2200)

    return ok, lt, errs

SKIP_DIRS  = {".git", "build", "__pycache__", ".github", "ai_dev", ".vscode", "node_modules"}
SKIP_FILES = {"screen.h.save", ".DS_Store", "Thumbs.db"}
SRC_EXTS   = {".c", ".h", ".asm", ".ld", ".s"}

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
    "ui/ui.h",
    "ui/ui.c",
    "apps/notepad.h",
    "apps/notepad.c",
    "apps/terminal.h",
    "apps/terminal.c",
    "apps/sysinfo.h",
    "apps/sysinfo.c",
    "apps/about.h",
    "apps/about.c",
    "Makefile",
    "linker.ld",
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
    af = sorted(set(CANONICAL_FILES + discover_files()))
    h  = hashlib.md5()
    for f in af:
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            try:
                st = os.stat(p)
                h.update(f"{f}:{st.st_mtime:.3f}:{st.st_size}".encode())
            except OSError:
                pass
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
    lines = ["=== CODE SOURCE MAXOS ===\n", "FICHIERS PRÉSENTS:\n"]
    for f, c in sources.items():
        lines.append(f"  {'✅' if c else '❌'} {f} ({len(c) if c else 0} chars)\n")
    lines.append("\n")
    header = "".join(lines)
    ctx    = header
    used   = len(ctx)

    prio = [
        "kernel/kernel.c",
        "kernel/kernel_entry.asm",
        "kernel/io.h",
        "Makefile",
        "linker.ld",
        "drivers/screen.h",
        "drivers/keyboard.h",
    ]
    done = set()
    for f in prio:
        c = sources.get(f, "")
        if not c:
            continue
        block = f"{'='*50}\nFICHIER: {f}\n{'='*50}\n{c}\n\n"
        if used + len(block) > max_chars:
            ctx  += f"[{f}: {len(c)} chars — tronqué]\n"
            done.add(f)
            continue
        ctx  += block
        used += len(block)
        done.add(f)

    for f, c in sources.items():
        if f in done or not c:
            continue
        block = f"{'='*50}\nFICHIER: {f}\n{'='*50}\n{c}\n\n"
        if used + len(block) > max_chars:
            ctx  += f"[{f}: {len(c)} chars — tronqué pour limite]\n"
            continue
        ctx  += block
        used += len(block)

    return ctx

def proj_stats(sources):
    files  = sum(1 for c in sources.values() if c)
    lines  = sum(c.count("\n") for c in sources.values() if c)
    chars  = sum(len(c) for c in sources.values() if c)
    by_ext = defaultdict(int)
    for f, c in sources.items():
        if c:
            ext = os.path.splitext(f)[1] or "other"
            by_ext[ext] += 1
    return {
        "files":  files,
        "lines":  lines,
        "chars":  chars,
        "by_ext": dict(by_ext),
    }

def analyze_quality(sources):
    bad_inc = [
        "stddef.h", "string.h", "stdlib.h", "stdio.h",
        "stdint.h", "stdbool.h", "stdarg.h", "stdnoreturn.h",
    ]
    bad_sym = [
        "size_t", "NULL", "bool", "true", "false",
        "uint32_t", "uint8_t", "uint16_t", "int32_t",
        "malloc", "free", "calloc", "realloc",
        "memset", "memcpy", "memmove", "strlen", "strcpy", "strcat",
        "printf", "sprintf", "fprintf", "puts",
    ]
    violations = []
    cf = af = 0
    for fname, content in sources.items():
        if not content:
            continue
        if fname.endswith((".c", ".h")):
            cf += 1
            for i, line in enumerate(content.split("\n"), 1):
                s = line.strip()
                if s.startswith(("//", "/*", "*", "#pragma")):
                    continue
                for inc in bad_inc:
                    if f"#include <{inc}>" in line or f'#include "{inc}"' in line:
                        violations.append(f"{fname}:{i} [INC] {inc}")
                for sym in bad_sym:
                    pat = r"\b" + re.escape(sym) + r"\b"
                    if re.search(pat, line):
                        violations.append(f"{fname}:{i} [SYM] {sym}")
                        break
        elif fname.endswith((".asm", ".s")):
            af += 1
            for i, line in enumerate(content.split("\n"), 1):
                s = line.strip().lower()
                if s.startswith(";"):
                    continue
                if "%rep" in s and ("global" in s or "isr" in s.split(":")[0] if ":" in s else "isr" in s):
                    violations.append(f"{fname}:{i} [ASM] %rep pour stubs ISR interdit")

    score = max(0, 100 - len(violations) * 3)
    return {
        "score":      score,
        "violations": violations[:35],
        "c_files":    cf,
        "asm_files":  af,
        "total_files": cf + af,
    }

def _safe_file_re(pattern):
    try:
        return re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        log(f"Regex compile error: {e} — pattern: {pattern[:80]}", "ERROR")
        return None

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
            if fn:
                to_del.append(fn)
                log(f"DELETE marqué: {fn}")
            continue

        start_m = FILE_START_RE.match(s)
        if start_m:
            if in_f and cur and lines:
                _commit_file(files, cur, lines)
            fn = start_m.group(1).strip()
            if fn and not fn.startswith("-") and len(fn) > 1:
                cur   = fn
                lines = []
                in_f  = True
            continue

        if FILE_END_RE.match(s) and in_f:
            if cur and lines:
                _commit_file(files, cur, lines)
            cur   = None
            lines = []
            in_f  = False
            continue

        if in_f:
            lines.append(raw_line)

    if in_f and cur and lines:
        _commit_file(files, cur, lines)

    if not files and not to_del:
        log(f"Parse: aucun fichier trouvé. Début réponse:\n{resp[:250]}", "WARN")
        if DEBUG:
            log(f"Réponse complète ({len(resp)} chars):\n{resp[:1000]}", "WARN")

    return files, to_del

def _commit_file(files_dict, path, lines):
    path    = path.strip().strip("`'\"")
    content = "\n".join(lines).strip()

    for fence in ("```c", "```asm", "```nasm", "```makefile", "```ld", "```bash", "```text", "```"):
        if content.startswith(fence):
            content = content[len(fence):].lstrip("\n")
            break
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
        path     = path.strip().strip("/").replace("\\", "/")
        full     = os.path.realpath(os.path.join(REPO_PATH, path))
        full_sep = full + (os.sep if os.path.isdir(full) else "")

        if not (full + os.sep).startswith(repo_real) and not full_sep.startswith(repo_real):
            if full != os.path.realpath(REPO_PATH):
                log(f"Path traversal bloqué: {path}", "ERROR")
                continue

        parent = os.path.dirname(full)
        if parent and parent != REPO_PATH:
            os.makedirs(parent, exist_ok=True)

        try:
            with open(full, "w", encoding="utf-8", newline="\n") as f:
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
        if not (full + os.sep).startswith(repo_real):
            log(f"Delete path traversal bloqué: {path}", "ERROR")
            continue
        if os.path.exists(full) and os.path.isfile(full):
            os.remove(full)
            deleted.append(path)
            log(f"Supprimé: {path}")
    SOURCE_CACHE["hash"] = None
    return deleted

def backup(paths):
    bak = {}
    for p in paths:
        full = os.path.join(REPO_PATH, p)
        if os.path.exists(full) and os.path.isfile(full):
            try:
                with open(full, "r", encoding="utf-8", errors="ignore") as f:
                    bak[p] = f.read()
            except Exception:
                pass
    return bak

def restore(bak):
    if not bak:
        return
    for p, c in bak.items():
        full   = os.path.join(REPO_PATH, p)
        parent = os.path.dirname(full)
        if parent:
            os.makedirs(parent, exist_ok=True)
        try:
            with open(full, "w", encoding="utf-8", newline="\n") as f:
                f.write(c)
        except Exception as e:
            log(f"Erreur restore {p}: {e}", "ERROR")
    log(f"Restauré {len(bak)} fichier(s)")
    SOURCE_CACHE["hash"] = None

OS_MISSION = (
    "MISSION MaxOS: OS bare metal x86 complet, moderne, stable.\n"
    "PROGRESSION: Boot→IDT+PIC→Timer PIT→Mémoire bitmap→"
    "VGA mode13h→Clavier IRQ→Terminal→FAT12→GUI desktop"
)

RULES = """╔══ RÈGLES BARE METAL x86 — VIOLATIONS = ÉCHEC BUILD ══╗
║ INCLUDES INTERDITS:                                    ║
║   stddef.h  string.h  stdlib.h  stdio.h               ║
║   stdint.h  stdbool.h  stdarg.h  stdnoreturn.h         ║
║                                                        ║
║ SYMBOLES INTERDITS:                                    ║
║   size_t  NULL  bool  true  false                      ║
║   uint32_t  uint8_t  uint16_t  int32_t                 ║
║   malloc  free  calloc  realloc                        ║
║   memset  memcpy  memmove  strlen  strcpy  strcat      ║
║   printf  sprintf  fprintf  puts                       ║
║                                                        ║
║ REMPLACEMENTS OBLIGATOIRES:                            ║
║   size_t    → unsigned int                             ║
║   NULL      → 0                                        ║
║   bool/true/false → int / 1 / 0                        ║
║   uint32_t  → unsigned int                             ║
║   uint8_t   → unsigned char                            ║
║   uint16_t  → unsigned short                           ║
║                                                        ║
║ TOOLCHAIN:                                             ║
║   GCC: -m32 -ffreestanding -fno-builtin               ║
║        -nostdlib -nostdinc -fno-pic -fno-pie           ║
║   NASM: -f elf (→.o) | -f bin (boot.bin)              ║
║   LD: ld -m elf_i386 -T linker.ld --oformat binary    ║
║                                                        ║
║ RÈGLES CRITIQUES:                                      ║
║   • io.h: SEUL fichier avec outb/inb (static inline)  ║
║     Ne JAMAIS redéfinir outb/inb ailleurs              ║
║   • isr.asm/handlers.asm: PAS de %macro/%rep pour     ║
║     les stubs — écrire isr0: isr1: ... isr47: MANUELS ║
║   • kernel_entry.asm: global _stack_top EN PREMIER     ║
║     puis resb 16384, puis global kernel_main           ║
║   • Tout nouveau .c → ajouter dans Makefile OBJS      ║
║   • ZÉRO commentaire dans le code généré              ║
║   • Chaque .c doit #include son propre .h             ║
╚════════════════════════════════════════════════════════╝"""

def default_plan():
    return {
        "score_actuel":   35,
        "niveau_os":      "Prototype bare metal",
        "fonctionnalites_presentes": [
            "Boot x86 (BIOS)", "VGA texte 80x25", "Clavier PS/2 polling", "4 apps basiques",
        ],
        "fonctionnalites_manquantes_critiques": [
            "IDT 256 + PIC 8259", "Timer PIT 8253", "Mémoire bitmap",
            "VGA mode 13h", "Clavier IRQ-driven", "FAT12",
        ],
        "prochaine_milestone": "Kernel stable IDT+Timer+Memory",
        "plan_ameliorations": [
            {
                "nom":                  "io.h + IDT 256 + PIC 8259 + ISR stubs",
                "priorite":             "CRITIQUE",
                "categorie":            "kernel",
                "fichiers_a_modifier":  ["kernel/kernel.c", "kernel/kernel_entry.asm", "Makefile"],
                "fichiers_a_creer":     ["kernel/io.h", "kernel/idt.h", "kernel/idt.c", "kernel/isr.asm"],
                "fichiers_a_supprimer": [],
                "description": (
                    "io.h: static inline void outb(unsigned short port, unsigned char val) { asm volatile(\"outb %0,%1\"::\"a\"(val),\"Nd\"(port)); } "
                    "static inline unsigned char inb(unsigned short port) { unsigned char v; asm volatile(\"inb %1,%0\":\"=a\"(v):\"Nd\"(port)); return v; } "
                    "idt.h: struct IDTEntry { unsigned short base_low; unsigned short sel; unsigned char zero; unsigned char flags; unsigned short base_high; } __attribute__((packed)); "
                    "struct IDTPtr { unsigned short limit; unsigned int base; } __attribute__((packed)); "
                    "void idt_init(void); "
                    "idt.c: static struct IDTEntry idt[256]; static struct IDTPtr idtp; "
                    "void idt_set_gate(unsigned char n, unsigned int base, unsigned short sel, unsigned char flags) { idt[n].base_low=base&0xFFFF; idt[n].sel=sel; idt[n].zero=0; idt[n].flags=flags; idt[n].base_high=(base>>16)&0xFFFF; } "
                    "PIC remap: outb(0x20,0x11) outb(0xA0,0x11) outb(0x21,0x20) outb(0xA1,0x28) outb(0x21,0x04) outb(0xA1,0x02) outb(0x21,0x01) outb(0xA1,0x01) outb(0x21,0xFF) outb(0xA1,0xFF) "
                    "asm(\"lidt [idtp]\"); "
                    "isr.asm: BITS 32. section .text. Écrire isr0: à isr47: EXPLICITEMENT (48 stubs). "
                    "Chaque stub sans errcode: push byte 0 / push byte N / jmp isr_common_stub. "
                    "Avec errcode (8,10-14,17): juste push byte N / jmp isr_common_stub. "
                    "isr_common_stub: pushad / push ds... / call isr_handler / ... / iret. "
                    "irq_common_stub: pareil + EOI (outb 0x20,0x20 et si irq>=8 outb 0xA0,0x20). "
                    "kernel_entry.asm: global _stack_top EN PREMIER. section .bss. _stack_top: resb 16384. "
                    "section .text. global kernel_main. kernel_main: mov esp,_stack_top / call kmain / cli / hlt. "
                    "kernel.c: kmain(): screen_init() idt_init() asm(\"sti\") boucle infinie."
                ),
                "impact_attendu": "OS stable, pas de triple fault, exceptions capturées",
                "complexite":     "HAUTE",
            },
            {
                "nom":                  "Timer PIT 8253 100Hz + sleep_ms volatile",
                "priorite":             "CRITIQUE",
                "categorie":            "kernel",
                "fichiers_a_modifier":  ["kernel/kernel.c", "Makefile"],
                "fichiers_a_creer":     ["kernel/timer.h", "kernel/timer.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "timer.h: void timer_init(void); unsigned int timer_ticks(void); void sleep_ms(unsigned int ms); "
                    "timer.c: volatile unsigned int g_ticks = 0; "
                    "timer_init(): diviseur=1193180/100=11931 → outb(0x43,0x36) outb(0x40,11931&0xFF) outb(0x40,(11931>>8)&0xFF); "
                    "idt_set_gate(32, (unsigned int)irq0_handler, 0x08, 0x8E); outb(0x21, inb(0x21) & ~0x01); "
                    "irq0_handler(): g_ticks++; outb(0x20,0x20); "
                    "timer_ticks(): return g_ticks; "
                    "sleep_ms(ms): unsigned int end = g_ticks + (ms/10); while(g_ticks < end) { asm volatile('hlt'); } "
                    "kernel.c: timer_init() après idt_init()."
                ),
                "impact_attendu": "Horloge système, sleep fonctionnel",
                "complexite":     "MOYENNE",
            },
            {
                "nom":                  "Allocateur mémoire bitmap 4KB pages",
                "priorite":             "HAUTE",
                "categorie":            "kernel",
                "fichiers_a_modifier":  ["kernel/kernel.c", "Makefile"],
                "fichiers_a_creer":     ["kernel/memory.h", "kernel/memory.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "memory.h: void mem_init(unsigned int start, unsigned int end); "
                    "unsigned int mem_alloc(void); void mem_free(unsigned int addr); "
                    "unsigned int mem_used(void); unsigned int mem_total(void); "
                    "memory.c: #define PAGE_SIZE 4096 #define MAX_PAGES 8192 "
                    "static unsigned int bitmap[MAX_PAGES/32]; "
                    "static unsigned int mem_start=0, mem_pages=0, used_pages=0; "
                    "mem_init: calcule mem_pages = (end-start)/PAGE_SIZE; "
                    "mem_alloc: cherche bit=0 dans bitmap, set bit, return addr; retourne 0 si plein. "
                    "mem_free: clear le bit correspondant à addr. "
                    "kernel.c: mem_init(0x400000, 0x2000000) après timer_init()."
                ),
                "impact_attendu": "Gestion mémoire physique pages 4KB",
                "complexite":     "HAUTE",
            },
            {
                "nom":                  "Terminal enrichi 25 commandes + historique",
                "priorite":             "HAUTE",
                "categorie":            "app",
                "fichiers_a_modifier":  ["apps/terminal.c", "apps/terminal.h"],
                "fichiers_a_creer":     [],
                "fichiers_a_supprimer": [],
                "description": (
                    "25 commandes: help ver mem uptime cls echo reboot halt color calc about "
                    "credits ps sysinfo license time date clear history env set beep disk cpu net. "
                    "Historique 32 entrées, navigation flèche haut/bas. "
                    "Complétion TAB basique. Couleurs ANSI par commande. "
                    "Signatutes: tm_init() tm_draw() tm_key(unsigned char k) tm_run(). "
                    "ZÉRO stdlib. Tout custom string compare/copy."
                ),
                "impact_attendu": "Terminal complet type cmd.exe / bash minimal",
                "complexite":     "MOYENNE",
            },
            {
                "nom":                  "VGA mode 13h 320x200 + desktop GUI",
                "priorite":             "NORMALE",
                "categorie":            "driver",
                "fichiers_a_modifier":  ["kernel/kernel.c", "drivers/screen.h", "drivers/screen.c", "Makefile"],
                "fichiers_a_creer":     ["drivers/vga.h", "drivers/vga.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "vga.h: void v_init(void); void v_pixel(int x,int y,unsigned char c); "
                    "void v_rect(int x,int y,int w,int h,unsigned char c); "
                    "void v_fill(unsigned char c); void v_hline(int x,int y,int w,unsigned char c); "
                    "void v_vline(int x,int y,int h,unsigned char c); "
                    "void v_char(int x,int y,unsigned char ch,unsigned char fg); "
                    "void v_string(int x,int y,const char* s,unsigned char fg); "
                    "void v_desktop(void); "
                    "vga.c: framebuffer=(unsigned char*)0xA0000; "
                    "v_init: outb(0x3C2,0x63); séquence VGA mode 13h complet (regs 0x3C4 0x3CE 0x3D4 0x3C0). "
                    "#include \"kernel/io.h\" — NE PAS redéfinir outb/inb. "
                    "v_desktop: fond bleu nuit (1), barre tâches grise (7) en bas 12px, "
                    "icônes apps en pixels, logo MaxOS en haut gauche. "
                    "Font 8x8 intégrée en tableau static unsigned char. "
                    "kernel.c: v_init() v_desktop() après mem_init()."
                ),
                "impact_attendu": "Interface graphique QEMU 320x200 couleurs",
                "complexite":     "HAUTE",
            },
        ],
    }

def _parse_json_robust(resp):
    if not resp:
        return None
    clean = resp.strip()

    if clean.startswith("```"):
        lines = clean.split("\n")
        end   = -1 if lines[-1].strip() == "```" else len(lines)
        clean = "\n".join(lines[1:end]).strip()

    i = clean.find("{")
    j = clean.rfind("}") + 1
    if i < 0 or j <= i:
        if DEBUG:
            log(f"_parse_json: pas de JSON trouvé dans: {clean[:150]}", "WARN")
        return None

    candidate = clean[i:j]

    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass

    fixed = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r'\\\\', candidate)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    fixed2 = re.sub(r',\s*([}\]])', r'\1', candidate)
    try:
        return json.loads(fixed2)
    except json.JSONDecodeError as ex:
        if DEBUG:
            log(f"_parse_json: échec final: {ex} — début: {candidate[:200]}", "WARN")
        return None

def phase_analyse(context, stats):
    log("=== PHASE 1: ANALYSE PROJET ===")
    disc_now(
        "🔍 Analyse en cours",
        f"`{stats['files']}` fichiers | `{stats['lines']:,}` lignes | `{stats['chars']:,}` chars",
        0x5865F2
    )

    prompt = (
        f"Tu es un expert OS bare metal x86. Analyse ce projet et retourne UNIQUEMENT du JSON valide.\n\n"
        f"{RULES}\n\n{OS_MISSION}\n\n"
        f"{context}\n\n"
        f"STATISTIQUES: {stats['files']} fichiers, {stats['lines']} lignes, {stats['chars']} chars\n\n"
        "RETOURNE UNIQUEMENT CE JSON (pas de texte avant ou après, commence directement par {):\n"
        '{\n'
        '  "score_actuel": 35,\n'
        '  "niveau_os": "description courte",\n'
        '  "fonctionnalites_presentes": ["feat1", "feat2"],\n'
        '  "fonctionnalites_manquantes_critiques": ["feat3"],\n'
        '  "prochaine_milestone": "titre milestone",\n'
        '  "plan_ameliorations": [\n'
        '    {\n'
        '      "nom": "Nom tâche",\n'
        '      "priorite": "CRITIQUE",\n'
        '      "categorie": "kernel",\n'
        '      "fichiers_a_modifier": ["kernel/kernel.c"],\n'
        '      "fichiers_a_creer": ["kernel/idt.h"],\n'
        '      "fichiers_a_supprimer": [],\n'
        '      "description": "specs techniques précises",\n'
        '      "impact_attendu": "résultat",\n'
        '      "complexite": "HAUTE"\n'
        '    }\n'
        '  ]\n'
        '}'
    )

    resp = ai_call(prompt, max_tokens=3500, timeout=70, tag="analyse")

    if not resp:
        log("Analyse IA indisponible → plan défaut utilisé", "WARN")
        disc_log("⚠️ Analyse", "IA indisponible → plan par défaut", 0xFF8800)
        return default_plan()

    log(f"Analyse: réponse {len(resp):,} chars reçue")

    result = _parse_json_robust(resp)
    if result and isinstance(result.get("plan_ameliorations"), list) and result["plan_ameliorations"]:
        nb    = len(result["plan_ameliorations"])
        score = result.get("score_actuel", "?")
        log(f"Analyse OK: score={score} | {nb} tâche(s) planifiées", "OK")
        return result

    log("JSON analyse invalide ou plan vide → plan par défaut", "WARN")
    disc_log("⚠️ Analyse JSON", "Réponse non parseable → plan défaut", 0xFF8800)
    return default_plan()

def task_ctx(task, sources):
    needed = set()
    needed.update(task.get("fichiers_a_modifier", []))
    needed.update(task.get("fichiers_a_creer", []))

    for f in list(needed):
        if f.endswith(".c"):
            needed.add(f.replace(".c", ".h"))
        elif f.endswith(".h"):
            needed.add(f.replace(".h", ".c"))

    always_include = [
        "kernel/kernel.c",
        "kernel/kernel_entry.asm",
        "kernel/io.h",
        "Makefile",
        "linker.ld",
        "drivers/screen.h",
        "drivers/keyboard.h",
    ]
    needed.update(always_include)

    ctx  = ""
    used = 0
    for f in sorted(needed):
        c = sources.get(f, "")
        if c:
            block = f"--- {f} ---\n{c}\n\n"
        else:
            block = f"--- {f} ---\n[FICHIER À CRÉER]\n\n"
        if used + len(block) > 24000:
            ctx  += f"[{f}: tronqué — {len(c) if c else 0} chars]\n"
            continue
        ctx  += block
        used += len(block)

    return ctx

def impl_prompt(task, ctx):
    nom  = task.get("nom", "?")
    cat  = task.get("categorie", "?")
    cx   = task.get("complexite", "MOYENNE")
    desc = task.get("description", "")
    fmod = task.get("fichiers_a_modifier", [])
    fnew = task.get("fichiers_a_creer", [])
    fdel = task.get("fichiers_a_supprimer", [])

    return (
        f"{RULES}\n\n"
        f"{'='*60}\n"
        f"TÂCHE: {nom}\n"
        f"CATÉGORIE: {cat} | COMPLEXITÉ: {cx}\n"
        f"FICHIERS À MODIFIER: {fmod}\n"
        f"FICHIERS À CRÉER: {fnew}\n"
        f"FICHIERS À SUPPRIMER: {fdel}\n"
        f"{'='*60}\n\n"
        f"SPÉCIFICATIONS TECHNIQUES:\n{desc}\n\n"
        f"CODE EXISTANT:\n{ctx}\n\n"
        f"{'='*60}\n"
        "CONTRAINTES SUPPLÉMENTAIRES ABSOLUES:\n"
        "1. isr.asm/idt_handlers.asm: JAMAIS de %macro/%rep pour stubs ISR\n"
        "   → Écrire chaque isr0:, isr1:, ..., isr47: EXPLICITEMENT ligne par ligne\n"
        "2. outb/inb: UNIQUEMENT dans kernel/io.h (static inline)\n"
        "   → Tout autre fichier fait #include \"kernel/io.h\"\n"
        "   → JAMAIS redéfinir outb ou inb dans vga.c, idt.c, timer.c, etc.\n"
        "3. kernel_entry.asm: 'global _stack_top' doit être la PREMIÈRE instruction\n"
        "4. Tout nouveau fichier .c doit apparaître dans Makefile OBJS\n"
        "5. ZÉRO commentaire dans le code\n"
        "6. Chaque .c commence par #include son propre .h\n"
        "7. Code 100% complet — ZÉRO '...', ZÉRO placeholder, ZÉRO TODO\n\n"
        "FORMAT DE SORTIE OBLIGATOIRE:\n"
        "=== FILE: chemin/relatif/fichier.ext ===\n"
        "[code source complet]\n"
        "=== END FILE ===\n\n"
        "COMMENCE LA GÉNÉRATION MAINTENANT:"
    )

def auto_fix(build_log, errs, gen_files, bak, model, max_att=4):
    log(f"Auto-fix démarré: {len(errs)} erreur(s) à corriger", "BUILD")
    _CYCLE_STATS["auto_fixes"] += 1

    cur_log  = build_log
    cur_errs = errs

    for att in range(1, max_att + 1):
        log(f"Fix {att}/{max_att} — {len(cur_errs)} err restantes", "BUILD")
        disc_log(f"🔧 Fix {att}/{max_att}", f"`{len(cur_errs)}` erreur(s)\n" + "\n".join(f"`{e[:60]}`" for e in cur_errs[:3]), 0x00AAFF)

        curr_files = {}
        for p in gen_files:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp) and os.path.isfile(fp):
                try:
                    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                        curr_files[p] = f.read()[:12000]
                except Exception:
                    pass

        file_ctx = "".join(f"--- {p} ---\n{c}\n\n" for p, c in curr_files.items())
        err_str  = "\n".join(cur_errs[:18])
        log_tail = cur_log[-3000:] if len(cur_log) > 3000 else cur_log

        diag_hints = []
        if "multiple definition" in err_str and ("outb" in err_str or "inb" in err_str):
            diag_hints.append("SOLUTION: outb/inb définis dans kernel/io.h uniquement — retirer du fichier fautif et faire #include \"kernel/io.h\"")
        if "identifier expected" in err_str and ("isr" in err_str or "global" in err_str.lower()):
            diag_hints.append("SOLUTION: Ne pas utiliser %macro/%rep pour les stubs ISR — écrire isr0: isr1: ... isr47: EXPLICITEMENT")
        if "undeclared" in err_str:
            symbols = re.findall(r"'(\w+)' undeclared", err_str)
            if symbols:
                diag_hints.append(f"SOLUTION: Ajouter les #include manquants pour: {', '.join(set(symbols[:8]))}")
        if "undefined reference" in err_str:
            funcs = re.findall(r"undefined reference to `(\w+)'", err_str)
            if funcs:
                diag_hints.append(f"SOLUTION: Vérifier que ces fichiers sont dans Makefile OBJS: {', '.join(set(funcs[:6]))}")
        if "_start" in err_str:
            diag_hints.append("SOLUTION: linker.ld doit avoir ENTRY(kernel_main) ou équivalent")

        hints_str = "\n".join(f"⚡ {h}" for h in diag_hints)

        prompt = (
            f"{RULES}\n\n"
            f"ERREURS DE COMPILATION À CORRIGER:\n```\n{err_str}\n```\n\n"
            f"FIN DU LOG BUILD:\n```\n{log_tail}\n```\n\n"
            f"DIAGNOSTICS:\n{hints_str}\n\n"
            f"FICHIERS ACTUELS (à corriger):\n{file_ctx}\n\n"
            "INSTRUCTIONS:\n"
            "- Corriger TOUTES les erreurs listées\n"
            "- ZÉRO commentaire, ZÉRO stdlib, code 100% complet\n"
            "- Si outb/inb multiple definition: faire #include \"kernel/io.h\" et supprimer la redéfinition\n"
            "- Si stubs ISR avec %rep/%macro: réécrire TOUS les stubs isr0: à isr47: manuellement\n\n"
            "FORMAT:\n=== FILE: fichier ===\n[code]\n=== END FILE ==="
        )

        resp = ai_call(prompt, max_tokens=32768, timeout=130, tag=f"fix/{att}")
        if not resp:
            wait = min(8 * (2 ** (att - 1)), 45)
            log(f"Fix {att}: réponse vide — attente {wait}s", "WARN")
            time.sleep(wait)
            continue

        new_files, _ = parse_ai_files(resp)
        if not new_files:
            log(f"Fix {att}: parse vide", "WARN")
            wait = min(5 * (2 ** (att - 1)), 30)
            time.sleep(wait)
            continue

        write_files(new_files)
        ok, cur_log, cur_errs = make_build()

        if ok:
            m_u = alive()[0]["model"] if alive() else model
            git_push("fix: build errors", list(new_files.keys()), f"auto-fix {len(errs)}err→0", m_u)
            disc_now("🔧 Fix ✅", f"**{len(errs)} err** → **0** en {att} tentative(s)", 0x00AAFF)
            _CYCLE_STATS["auto_fix_success"] += 1
            return True, {"attempts": att, "fixed_files": list(new_files.keys())}

        log(f"Fix {att}: {len(cur_errs)} erreur(s) restantes", "WARN")
        wait = min(6 * (2 ** (att - 1)), 35)
        time.sleep(wait)

    restore(bak)
    _CYCLE_STATS["auto_fix_fail"] += 1
    return False, {"attempts": max_att, "remaining_errors": cur_errs[:5]}

def pre_flight_check():
    log("Pre-flight: vérification build initial...", "BUILD")
    ok, log_text, errs = make_build()
    if not ok:
        log(f"Pre-flight: build déjà cassé ({len(errs)} err) — correction avant de commencer", "WARN")
        disc_now(
            "⚠️ Build pré-existant cassé",
            f"`{len(errs)}` erreur(s) avant toute modification\n" +
            "\n".join(f"`{e[:75]}`" for e in errs[:4]),
            0xFF6600
        )
        return False, errs
    log("Pre-flight: build OK ✅", "OK")
    return True, []

def implement(task, sources, i, total):
    nom   = task.get("nom", f"Tâche {i}")
    cat   = task.get("categorie", "?")
    prio  = task.get("priorite", "?")
    cx    = task.get("complexite", "MOYENNE")
    desc  = task.get("description", "")
    f_mod = task.get("fichiers_a_modifier", [])
    f_new = task.get("fichiers_a_creer", [])
    model = alive()[0]["model"] if alive() else "?"

    log(f"\n{'='*56}\n[{i}/{total}] [{prio}] {nom}\n{'='*56}")

    disc_now(
        f"🚀 [{i}/{total}] {nom[:55]}",
        f"```\n{pbar(int((i - 1) / total * 100))}\n```\n{desc[:280]}",
        0xFFA500,
        [
            {"name": "🎯 Priorité",   "value": prio,  "inline": True},
            {"name": "📁 Catégorie",  "value": cat,   "inline": True},
            {"name": "⚙️ Complexité", "value": cx,    "inline": True},
            {"name": "📝 Modifier",
             "value": "\n".join(f"`{f}`" for f in f_mod[:5]) or "—",
             "inline": True},
            {"name": "✨ Créer",
             "value": "\n".join(f"`{f}`" for f in f_new[:5]) or "—",
             "inline": True},
            {"name": "🔑 Providers",  "value": prov_summary()[:400], "inline": False},
        ]
    )

    t0      = time.time()
    ctx     = task_ctx(task, sources)
    max_tok = {"HAUTE": 32768, "MOYENNE": 24576, "BASSE": 12288}.get(cx, 24576)
    prompt  = impl_prompt(task, ctx)

    resp    = ai_call(prompt, max_tokens=max_tok, timeout=180, tag=f"impl/{nom[:16]}")
    elapsed = round(time.time() - t0, 1)

    if not resp:
        disc_now(
            f"❌ [{i}/{total}] {nom[:50]}",
            f"Tous les providers indisponibles après {elapsed}s",
            0xFF4444
        )
        return False, [], [], {
            "nom": nom, "elapsed": elapsed, "result": "ai_fail",
            "errors": [], "model": model,
        }

    files, to_del = parse_ai_files(resp)

    if not files and not to_del:
        disc_now(
            f"❌ [{i}/{total}] {nom[:50]}",
            f"Réponse reçue ({len(resp):,}c) mais aucun fichier parsé",
            0xFF6600,
            [{"name": "Début réponse", "value": f"```\n{resp[:300]}\n```", "inline": False}]
        )
        return False, [], [], {
            "nom": nom, "elapsed": elapsed, "result": "parse_empty",
            "errors": [], "model": model,
        }

    disc_log(
        f"📁 {len(files)} fichier(s) générés",
        "\n".join(f"`{f}` → {len(c):,}c" for f, c in list(files.items())[:10]),
        0x00AAFF
    )

    bak_f   = backup(list(files.keys()))
    written = write_files(files)
    deleted = del_files(to_del)

    if not written and not deleted:
        return False, [], [], {
            "nom": nom, "elapsed": elapsed, "result": "no_files_written",
            "errors": [], "model": model,
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
            fs_str = "\n".join(f"`{f}`" for f in (written + deleted)[:8]) or "—"
            disc_now(
                f"✅ [{i}/{total}] {nom[:50]}",
                f"```\n{pbar(int(i / total * 100))}\n```\nCommit: `{sha}`",
                0x00FF88,
                [
                    {"name": "⏱️ Durée",   "value": f"{total_elapsed:.0f}s",       "inline": True},
                    {"name": "📁 Fichiers","value": str(len(written + deleted)),    "inline": True},
                    {"name": "🤖 Modèle", "value": model[:30],                     "inline": True},
                    {"name": "📝 Commits", "value": f"`{sha}`",                    "inline": True},
                    {"name": "📁 Liste",   "value": fs_str,                        "inline": False},
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
            disc_log(f"✅ [{i}/{total}] {nom[:50]} (déjà à jour)", "", 0x00AA44)
            return True, [], [], m
        else:
            restore(bak_f)
            return False, [], [], {
                "nom": nom, "elapsed": elapsed, "result": "push_fail",
                "errors": [], "model": model,
            }

    fixed, fix_meta = auto_fix(build_log, errs, list(files.keys()), bak_f, model)

    if fixed:
        total_elapsed = round(time.time() - t0, 1)
        fc            = fix_meta.get("attempts", 0)
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
            f"```\n{pbar(int(i / total * 100))}\n```\nCorrigé en {fc} tentative(s)",
            0x00BB66,
            [
                {"name": "⏱️", "value": f"{total_elapsed:.0f}s", "inline": True},
                {"name": "🔧", "value": f"{fc} fix",             "inline": True},
                {"name": "🤖", "value": model[:30],              "inline": True},
            ]
        )
        return True, written, deleted, m

    restore(bak_f)
    for p in written:
        if p not in bak_f:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp) and os.path.isfile(fp):
                try:
                    os.remove(fp)
                except Exception:
                    pass
    SOURCE_CACHE["hash"] = None

    total_elapsed = round(time.time() - t0, 1)
    remaining_errs = fix_meta.get("remaining_errors", errs[:5])
    es = "\n".join(f"`{e[:80]}`" for e in remaining_errs[:5])

    disc_now(
        f"❌ [{i}/{total}] {nom[:50]}",
        f"Build fail après {fix_meta.get('attempts',0)} fix(es) — restauré",
        0xFF4444,
        [
            {"name": "Erreurs",  "value": es[:900] or "?",         "inline": False},
            {"name": "⏱️ Durée", "value": f"{total_elapsed:.0f}s", "inline": True},
            {"name": "🔧 Fixes", "value": str(fix_meta.get("attempts",0)), "inline": True},
        ]
    )
    return False, [], [], {
        "nom":     nom,
        "elapsed": total_elapsed,
        "result":  "build_fail",
        "errors":  remaining_errs[:5],
        "model":   model,
    }

BOT_LOGINS = frozenset({
    "MaxOS-AI-Bot", "github-actions[bot]",
    "dependabot[bot]", "maxos-ai[bot]", "renovate[bot]",
})

def _bot_already_commented(n):
    comments = gh_issue_comments(n)
    return any(
        c.get("user", {}).get("login", "") in BOT_LOGINS
        for c in (comments or [])
    )

def handle_issues(ms_cache=None):
    if ms_cache is None:
        ms_cache = {}
    issues = gh_open_issues()
    if not issues:
        log("Issues: aucune issue ouverte")
        return
    log(f"Issues: {len(issues)} ouverte(s)")

    treated = 0
    for issue in issues[:15]:
        n      = issue.get("number")
        title  = issue.get("title", "")
        author = issue.get("user", {}).get("login", "")
        body_t = (issue.get("body", "") or "")[:1000]
        labels = [l.get("name", "") for l in issue.get("labels", [])]
        state  = issue.get("state", "open")

        if state != "open":
            continue
        if author in BOT_LOGINS:
            continue
        if _bot_already_commented(n):
            log(f"Issue #{n}: déjà traitée, skip")
            continue
        if not watchdog():
            break

        log(f"Issue #{n}: {title[:65]}")

        prompt = (
            f"Tu es le bot GitHub de MaxOS, un OS bare metal x86.\n"
            f"ISSUE #{n}\nTitre: {title}\nAuteur: {author}\n"
            f"Labels: {', '.join(labels) or 'aucun'}\n"
            f"Corps:\n{body_t}\n\n"
            "Réponds UNIQUEMENT avec ce JSON valide (rien d'autre):\n"
            '{\n'
            '  "type": "bug|enhancement|question|invalid|duplicate|wontfix",\n'
            '  "priority": "critical|high|medium|low",\n'
            '  "component": "kernel|driver|app|build|doc|other",\n'
            '  "labels_add": ["bug"],\n'
            '  "milestone": "Kernel stable IDT+Timer+Memory",\n'
            '  "action": "respond|close|close_not_planned|label_only|needs_info",\n'
            '  "response": "réponse utile et détaillée en français",\n'
            '  "duplicate_of": null,\n'
            '  "assignees": []\n'
            '}'
        )

        a = _parse_json_robust(ai_call(prompt, max_tokens=900, timeout=40, tag=f"issue/{n}"))
        if not a:
            log(f"Issue #{n}: analyse IA échouée", "WARN")
            continue

        action    = a.get("action", "label_only")
        lbl_add   = [l for l in a.get("labels_add", []) if l in STANDARD_LABELS]
        resp_t    = a.get("response", "")
        itype     = a.get("type", "?")
        component = a.get("component", "other")
        ms_title  = a.get("milestone", "")
        dup_of    = a.get("duplicate_of")

        if component in STANDARD_LABELS and component not in lbl_add:
            lbl_add.append(component)
        if "ai-reviewed" not in lbl_add:
            lbl_add.append("ai-reviewed")
        if lbl_add:
            gh_add_labels(n, lbl_add)

        if ms_title and ms_title not in ("null", "", "none"):
            if ms_title not in ms_cache:
                ms_cache[ms_title] = gh_ensure_milestone(ms_title)
            ms_num = ms_cache.get(ms_title)
            if ms_num:
                gh_assign_ms(n, ms_num)

        model_u = alive()[0]["model"] if alive() else "?"
        if resp_t and action in ("respond", "close", "close_not_planned", "needs_info"):
            dup_note = f"\n\n> ℹ️ Possible doublon de #{dup_of}" if dup_of else ""
            info_req = "\n\n> 📋 Merci de fournir plus d'informations pour continuer." if action == "needs_info" else ""
            comment  = (
                f"## 🤖 MaxOS AI — Analyse automatique\n\n"
                f"{resp_t}{dup_note}{info_req}\n\n"
                f"---\n"
                f"*Type: `{itype}` | Composant: `{component}` | Priorité: `{a.get('priority','?')}` | "
                f"Modèle: {model_u} | MaxOS AI v{VERSION}*"
            )
            gh_post_comment(n, comment)

        if action == "close":
            gh_close_issue(n, "completed")
            log(f"Issue #{n}: fermée (completed)")
        elif action == "close_not_planned":
            gh_close_issue(n, "not_planned")
            log(f"Issue #{n}: fermée (not_planned)")

        disc_log(f"🎫 Issue #{n} — {itype}", f"**{title[:45]}**\n`{action}` | `{component}`", 0x5865F2)
        treated += 1
        time.sleep(1)

    log(f"Issues: {treated} traitée(s)")
    return ms_cache

def handle_stale(days_stale=21, days_close=7):
    issues  = gh_open_issues()
    now     = time.time()
    ss      = days_stale * 86400
    cs      = (days_stale + days_close) * 86400
    marked  = closed = 0

    for issue in issues:
        n      = issue.get("number")
        upd    = issue.get("updated_at", "")
        labels = [l.get("name", "") for l in issue.get("labels", [])]
        author = issue.get("user", {}).get("login", "")
        title  = issue.get("title", "")

        if author in BOT_LOGINS:
            continue
        if any(l in labels for l in ("wontfix", "security", "bug")):
            continue

        is_stale = "stale" in labels
        try:
            upd_ts = datetime.strptime(upd, "%Y-%m-%dT%H:%M:%SZ").timestamp()
        except Exception:
            continue
        age = now - upd_ts

        if age >= cs and is_stale:
            gh_post_comment(
                n,
                f"🤖 **MaxOS AI**: Fermeture automatique après **{int(age/86400)} jours** d'inactivité.\n\n"
                f"Si cette issue est encore pertinente, merci de la rouvrir avec plus de contexte."
            )
            gh_close_issue(n, "not_planned")
            closed += 1
            log(f"Issue #{n} '{title[:40]}': fermée (stale {int(age/86400)}j)")

        elif age >= ss and not is_stale:
            gh_add_labels(n, ["stale"])
            gh_post_comment(
                n,
                f"⏰ **MaxOS AI**: Cette issue est inactive depuis **{int(age/86400)} jours**.\n\n"
                f"Elle sera fermée automatiquement dans **{days_close} jours** sans activité.\n"
                f"Commentez pour la maintenir ouverte !"
            )
            marked += 1
            log(f"Issue #{n} '{title[:40]}': marquée stale ({int(age/86400)}j)")

    if marked + closed > 0:
        log(f"Stale: {marked} marquées, {closed} fermées")
        disc_log("⏰ Stale Bot", f"**{marked}** marquées stale | **{closed}** fermées", 0xAAAAAA)

def handle_prs():
    prs = gh_open_prs()
    if not prs:
        log("PRs: aucune pull request ouverte")
        return
    log(f"PRs: {len(prs)} ouverte(s)")

    reviewed = 0
    for pr in prs[:8]:
        n      = pr.get("number")
        title  = pr.get("title", "")
        author = pr.get("user", {}).get("login", "")
        state  = pr.get("state", "open")

        if state != "open":
            continue
        if author in BOT_LOGINS:
            continue
        revs = gh_pr_reviews(n)
        if any(r.get("user", {}).get("login", "") in BOT_LOGINS for r in (revs or [])):
            log(f"PR #{n}: déjà reviewée, skip")
            continue
        if not watchdog():
            break

        log(f"PR #{n}: {title[:65]}")

        files_d = gh_pr_files(n)
        commits = gh_pr_commits(n)
        pr_info = gh_api("GET", f"pulls/{n}") or pr

        file_list = "\n".join(
            f"- `{f.get('filename','?')}` (+{f.get('additions',0)} -{f.get('deletions',0)})"
            for f in files_d[:20]
        )
        patches = ""
        for f in files_d[:6]:
            if f.get("filename", "").endswith((".c", ".h", ".asm")):
                p = f.get("patch", "")[:2000]
                if p:
                    patches += f"\n--- {f.get('filename','')} ---\n{p}\n"

        commit_list = "\n".join(
            f"- {c.get('commit',{}).get('message','').split(chr(10))[0][:85]}"
            for c in (commits or [])[:10]
        )

        is_draft = pr_info.get("draft", False)
        base_sha = pr_info.get("base", {}).get("sha", "")[:7]
        head_sha = pr_info.get("head", {}).get("sha", "")[:7]

        prompt = (
            f"Tu es un expert code review pour MaxOS, OS bare metal x86.\n"
            f"{RULES}\n\n"
            f"PR #{n}: {title}\nAuteur: {author}\n"
            f"Draft: {'Oui' if is_draft else 'Non'} | Base: {base_sha} → Head: {head_sha}\n\n"
            f"Fichiers modifiés ({len(files_d)}):\n{file_list}\n\n"
            f"Commits ({len(commits or [])}):\n{commit_list}\n\n"
            f"Extraits diff:\n{patches}\n\n"
            "Réponds UNIQUEMENT avec ce JSON valide:\n"
            '{\n'
            '  "decision": "APPROVE|REQUEST_CHANGES|COMMENT",\n'
            '  "summary": "résumé 2-3 phrases",\n'
            '  "problems": ["problème 1"],\n'
            '  "positives": ["point positif 1"],\n'
            '  "bare_metal_violations": ["violation 1"],\n'
            '  "security_issues": [],\n'
            '  "performance_notes": [],\n'
            '  "inline_comments": [{"path": "kernel/idt.c", "line": 10, "body": "commentaire"}],\n'
            '  "merge_safe": false,\n'
            '  "merge_after_fixes": false\n'
            '}'
        )

        a = _parse_json_robust(ai_call(prompt, max_tokens=3000, timeout=65, tag=f"pr/{n}"))
        if not a:
            a = {}

        decision   = a.get("decision", "COMMENT")
        merge_safe = a.get("merge_safe", False)
        summary    = a.get("summary", "Analyse non disponible.")
        problems   = a.get("problems", [])
        positives  = a.get("positives", [])
        viols      = a.get("bare_metal_violations", [])
        sec_issues = a.get("security_issues", [])
        perf_notes = a.get("performance_notes", [])
        inlines    = a.get("inline_comments", [])

        if is_draft and decision == "APPROVE":
            decision = "COMMENT"

        icon = {"APPROVE": "✅", "REQUEST_CHANGES": "🔴", "COMMENT": "💬"}.get(decision, "💬")
        safe = "🟢 Prêt à merger" if merge_safe else "🔴 À ne pas merger"

        body = f"## {icon} Code Review MaxOS AI — PR #{n}\n\n> **{decision}** | {safe}\n\n{summary}\n\n"
        if is_draft:
            body += "> ⚠️ PR en mode Draft — review préliminaire uniquement\n\n"
        if problems:
            body += "### ❌ Problèmes détectés\n" + "\n".join(f"- {p}" for p in problems[:8]) + "\n\n"
        if viols:
            body += "### ⚠️ Violations bare metal\n" + "\n".join(f"- `{v}`" for v in viols[:8]) + "\n\n"
        if sec_issues:
            body += "### 🔒 Problèmes sécurité\n" + "\n".join(f"- {s}" for s in sec_issues[:5]) + "\n\n"
        if positives:
            body += "### ✅ Points positifs\n" + "\n".join(f"- {p}" for p in positives[:6]) + "\n\n"
        if perf_notes:
            body += "### ⚡ Performance\n" + "\n".join(f"- {p}" for p in perf_notes[:4]) + "\n\n"

        model_u = alive()[0]["model"] if alive() else "?"
        body   += f"\n---\n*MaxOS AI v{VERSION} | {model_u} | Review automatique*"

        review_labels = ["ai-reviewed"]
        if decision == "APPROVE" and merge_safe and not is_draft:
            gh_approve_pr(n, body)
            review_labels.append("ai-approved")
        elif decision == "REQUEST_CHANGES":
            gh_req_changes(n, body, inlines if inlines else None)
            review_labels += ["ai-rejected", "needs-fix"]
        else:
            gh_post_review(n, body, "COMMENT", inlines if inlines else None)

        cat_labels = set()
        for f in files_d[:12]:
            fn = f.get("filename", "")
            if "kernel/" in fn: cat_labels.add("kernel")
            if "drivers/" in fn: cat_labels.add("driver")
            if "apps/" in fn: cat_labels.add("app")
            if "boot/" in fn: cat_labels.add("boot")
        if cat_labels:
            review_labels += list(cat_labels)

        gh_add_labels(n, list(set(review_labels)))

        color = (0x00AAFF if decision == "APPROVE"
                 else 0xFF4444 if decision == "REQUEST_CHANGES"
                 else 0xFFA500)
        disc_log(f"📋 PR #{n} — {decision}", f"**{title[:45]}** | {safe}", color)
        log(f"PR #{n} → {decision} ({safe})")
        reviewed += 1
        time.sleep(1)

    log(f"PRs: {reviewed} reviewée(s)")

def create_release(tasks_done, tasks_failed, analyse, stats):
    releases = gh_list_releases(10)
    last_tag  = "v0.0.0"
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

    score = analyse.get("score_actuel", 35)
    if score >= 80:
        major += 1; minor = 0; patch = 0
    elif score >= 60:
        minor += 1; patch = 0
    else:
        patch += 1
    new_tag = f"v{major}.{minor}.{patch}"

    niveau   = analyse.get("niveau_os", "?")
    ms       = analyse.get("prochaine_milestone", "?")
    features = analyse.get("fonctionnalites_presentes", [])

    compare   = gh_compare(last_tag, "HEAD")
    commits   = compare.get("commits", [])
    ahead_by  = compare.get("ahead_by", len(commits))
    chg_lines = []
    for c in commits[:25]:
        sha  = c.get("sha", "")[:7]
        msg  = c.get("commit", {}).get("message", "").split("\n")[0][:85]
        if msg and not msg.startswith("[skip"):
            chg_lines.append(f"- `{sha}` {msg}")
    changelog = "\n".join(chg_lines) or "- Maintenance et corrections"

    changes_ok = "".join(
        f"- ✅ **{t.get('nom','?')[:55]}** "
        f"[`{t.get('sha','?')[:7]}`] "
        f"*{t.get('model','?')[:20]}*"
        f"{' (fix×'+str(t['fix_count'])+')' if t.get('fix_count',0)>0 else ''}"
        f" — {t.get('elapsed',0):.0f}s\n"
        for t in tasks_done
    )
    changes_fail = (
        "\n## ⏭️ Reporté à la prochaine version\n\n" +
        "\n".join(f"- ❌ {n}" for n in tasks_failed) + "\n"
        if tasks_failed else ""
    )
    feat_txt = "\n".join(f"- ✅ {f}" for f in features[:10]) or "- (aucune)"

    tk      = sum(p["tokens"] for p in PROVIDERS)
    calls   = sum(p["calls"]  for p in PROVIDERS)
    types   = ", ".join(sorted({p["type"] for p in PROVIDERS if p["calls"] > 0})) or "?"
    elapsed = int(time.time() - START_TIME)
    now     = datetime.utcnow()

    repo_info = gh_repo_info()

    prov_perf = ""
    for p in sorted(PROVIDERS, key=lambda x: -x["calls"]):
        if p["calls"] == 0:
            continue
        avg = avg_rt(p)
        st  = "💀" if p["dead"] else "🟢"
        prov_perf += f"| {st} `{p['id']}` | {p['calls']} | ~{p['tokens']:,} | {avg:.1f}s |\n"

    cycle_info = (
        f"| Total appels IA | {_CYCLE_STATS.get('ai_calls',0)} |\n"
        f"| Échecs IA | {_CYCLE_STATS.get('ai_failures',0)} |\n"
        f"| Total 429 | {_CYCLE_STATS.get('total_429',0)} |\n"
        f"| Commits | {_CYCLE_STATS.get('total_commits',0)} |\n"
        f"| Builds OK | {_CYCLE_STATS.get('builds_ok',0)} |\n"
        f"| Builds fail | {_CYCLE_STATS.get('builds_fail',0)} |\n"
        f"| Auto-fix OK | {_CYCLE_STATS.get('auto_fix_success',0)} |\n"
        f"| Auto-fix fail | {_CYCLE_STATS.get('auto_fix_fail',0)} |\n"
        f"| Attentes cooldown | {_CYCLE_STATS.get('total_waits',0)} ({_CYCLE_STATS.get('total_wait_secs',0)}s) |\n"
        f"| Tokens totaux | ~{tk:,} |\n"
        f"| Durée cycle | {elapsed}s |\n"
    )

    body = (
        f"# 🖥️ MaxOS {new_tag}\n\n"
        f"> 🤖 Généré automatiquement par **MaxOS AI v{VERSION}**\n\n"
        f"---\n\n"
        f"## 📊 État du projet\n\n"
        f"| Métrique | Valeur |\n|---|---|\n"
        f"| 🎯 Score qualité | **{score}/100** |\n"
        f"| 📈 Niveau | {niveau} |\n"
        f"| 📁 Fichiers sources | {stats.get('files',0)} |\n"
        f"| 📝 Lignes de code | {stats.get('lines',0):,} |\n"
        f"| 🎯 Prochaine milestone | {ms} |\n"
        f"| ⭐ Stars | {repo_info.get('stars',0)} |\n"
        f"| 🍴 Forks | {repo_info.get('forks',0)} |\n"
        f"| 📦 Taille | {repo_info.get('size_kb',0)} KB |\n\n"
        f"## ✅ Améliorations cette version ({len(tasks_done)})\n\n"
        f"{changes_ok or '*(aucune)*'}"
        f"{changes_fail}\n"
        f"## 🧩 Fonctionnalités présentes\n\n{feat_txt}\n\n"
        f"## 📝 Changelog {last_tag} → {new_tag} ({ahead_by} commits)\n\n{changelog}\n\n"
        f"## 🚀 Tester\n\n"
        f"```bash\n"
        f"# QEMU\n"
        f"qemu-system-i386 -drive format=raw,file=os.img,if=floppy -boot a -vga std -k fr -m 32\n\n"
        f"# Bochs\n"
        f"bochs -q 'boot:a' 'floppya: 1_44=os.img, status=inserted'\n"
        f"```\n\n"
        f"## 🤖 Statistiques IA & Cycle\n\n"
        f"| Métrique | Valeur |\n|---|---|\n"
        f"{cycle_info}\n"
        f"### Providers utilisés\n\n"
        f"| Status | Provider | Appels | Tokens | Avg RT |\n|---|---|---|---|---|\n"
        f"{prov_perf or '*(aucun appel)*'}\n"
        f"---\n*MaxOS AI v{VERSION} | {now.strftime('%Y-%m-%d %H:%M')} UTC | {types}*\n"
    )

    pre = score < 50
    url = gh_create_release(
        new_tag,
        f"MaxOS {new_tag} — {niveau} — {now.strftime('%Y-%m-%d')}",
        body,
        pre=pre
    )

    if url:
        disc_now(
            f"🚀 Release {new_tag} publiée !",
            f"Score: **{score}/100** | {niveau}\n{'⚠️ Pre-release' if pre else '✅ Release stable'}",
            0x00FF88 if not pre else 0xFFA500,
            [
                {"name": "🏷️ Version",  "value": new_tag,               "inline": True},
                {"name": "📊 Score",    "value": f"{score}/100",         "inline": True},
                {"name": "📁 Fichiers", "value": str(stats.get("files",0)), "inline": True},
                {"name": "✅ Tâches",   "value": str(len(tasks_done)),   "inline": True},
                {"name": "❌ Reportées","value": str(len(tasks_failed)), "inline": True},
                {"name": "🔗 Lien",     "value": f"[Voir la release]({url})", "inline": False},
            ]
        )
        log(f"Release {new_tag} créée: {url}", "OK")
    else:
        log("Release: échec de création", "ERROR")

    return url

def final_report(success, total, tasks_done, tasks_failed, analyse, stats):
    score   = analyse.get("score_actuel", 35)
    niveau  = analyse.get("niveau_os", "?")
    pct     = int(success / total * 100) if total > 0 else 0
    color   = 0x00FF88 if pct >= 80 else 0xFFA500 if pct >= 50 else 0xFF4444
    elapsed = int(time.time() - START_TIME)
    tk      = sum(p["tokens"] for p in PROVIDERS)
    calls   = sum(p["calls"]  for p in PROVIDERS)

    sources = read_all()
    qual    = analyze_quality(sources)

    done_s = "\n".join(
        f"✅ {t.get('nom','?')[:42]} ({t.get('elapsed',0):.0f}s)"
        + (f" fix×{t['fix_count']}" if t.get("fix_count", 0) > 0 else "")
        for t in tasks_done
    ) or "Aucune"

    fail_s = "\n".join(f"❌ {n[:42]}" for n in tasks_failed) or "Aucune"

    prov_lines = []
    for p in sorted(PROVIDERS, key=lambda x: -x["calls"]):
        if p["calls"] == 0:
            continue
        st = "💀" if p["dead"] else "🟢"
        prov_lines.append(
            f"{st} `{p['id']}` {p['calls']}c ~{p['tokens']:,}tk avg{avg_rt(p):.0f}s sr{p['success_rate']:.2f}"
        )

    disc_now(
        f"🏁 Cycle terminé — {success}/{total} tâches",
        f"```\n{pbar(pct)}\n```\n**{pct}% de réussite**",
        color,
        [
            {"name": "✅ Succès",    "value": str(success),              "inline": True},
            {"name": "❌ Échecs",    "value": str(total - success),      "inline": True},
            {"name": "📈 Taux",      "value": f"{pct}%",                 "inline": True},
            {"name": "⏱️ Durée",     "value": f"{elapsed}s ({uptime()})", "inline": True},
            {"name": "🔑 Appels IA", "value": str(calls),               "inline": True},
            {"name": "💬 ~Tokens",   "value": f"{tk:,}",                "inline": True},
            {"name": "🔁 429 total", "value": str(_CYCLE_STATS.get("total_429",0)), "inline": True},
            {"name": "📊 Qualité",   "value": f"{qual['score']}/100",   "inline": True},
            {"name": "📁 Fichiers",  "value": str(stats.get("files",0)),"inline": True},
            {"name": "📝 Lignes",    "value": f"{stats.get('lines',0):,}","inline": True},
            {"name": "🏆 Score OS",  "value": f"{score}/100 — {niveau}", "inline": False},
            {"name": "✅ Réussies",  "value": done_s[:900],              "inline": False},
            {"name": "❌ Échouées",  "value": fail_s[:500],              "inline": False},
            {"name": "🔑 Providers", "value": prov_summary()[:600],     "inline": False},
            {"name": "📡 Détail",    "value": "\n".join(prov_lines[:8])[:700] or "—", "inline": False},
        ]
    )

    if qual["violations"]:
        disc_now(
            f"⚠️ {len(qual['violations'])} violation(s) bare metal",
            "```\n" + "\n".join(f"• {v}" for v in qual["violations"][:18]) + "\n```",
            0xFF6600
        )

def main():
    print("=" * 64)
    print(f"  MaxOS AI Developer v{VERSION}")
    print(f"  Ultra-robuste | Multi-provider | Bare metal x86 | GitHub")
    print("=" * 64)

    if not PROVIDERS:
        print("FATAL: Aucun provider IA configuré.")
        print("  Secrets requis: GEMINI_API_KEY, OPENROUTER_KEY, GROQ_KEY, MISTRAL_KEY")
        sys.exit(1)

    by_type = defaultdict(list)
    for p in PROVIDERS:
        by_type[p["type"]].append(p)
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
        f"`{len(PROVIDERS)}` providers IA configurés",
        0x5865F2,
        [
            {"name": "🔑 Providers", "value": prov_summary()[:800],       "inline": False},
            {"name": "📁 Repo",      "value": f"`{REPO_OWNER}/{REPO_NAME}`", "inline": True},
            {"name": "⏱️ Runtime",   "value": f"{MAX_RUNTIME}s max",      "inline": True},
            {"name": "🐛 Debug",     "value": "ON" if DEBUG else "OFF",   "inline": True},
        ]
    )

    subprocess.run(["make", "clean"], cwd=REPO_PATH, capture_output=True, timeout=30)

    log("Setup: création labels GitHub...")
    gh_ensure_labels(STANDARD_LABELS)

    ms_cache = {}

    log("[Issues] Traitement des issues ouvertes...")
    ms_cache = handle_issues(ms_cache) or ms_cache
    if not watchdog():
        sys.exit(0)

    log("[Stale] Vérification issues inactives...")
    handle_stale(days_stale=21, days_close=7)
    if not watchdog():
        sys.exit(0)

    log("[PRs] Traitement des pull requests...")
    handle_prs()
    if not watchdog():
        sys.exit(0)

    log("[Pre-flight] Vérification build initial...")
    pf_ok, pf_errs = pre_flight_check()
    if not pf_ok:
        log(f"Build pré-existant cassé: {len(pf_errs)} err. Tentative de correction...", "WARN")

    sources = read_all(force=True)
    stats   = proj_stats(sources)
    qual    = analyze_quality(sources)

    log(f"Sources: {stats['files']} fichiers | {stats['lines']:,} lignes | {stats['chars']:,} chars")
    log(f"Qualité: {qual['score']}/100 | {len(qual['violations'])} violation(s) | {qual['c_files']} .c | {qual['asm_files']} .asm")

    disc_now(
        "📊 Sources analysées",
        f"`{stats['files']}` fichiers | `{stats['lines']:,}` lignes",
        0x5865F2,
        [
            {"name": "Qualité",   "value": f"{qual['score']}/100 ({len(qual['violations'])} violations)", "inline": True},
            {"name": "Fichiers C","value": f"{qual['c_files']} .c/.h",  "inline": True},
            {"name": "ASM",       "value": f"{qual['asm_files']} .asm", "inline": True},
            {"name": "Ext",       "value": str(stats.get("by_ext", {}))[:200], "inline": False},
        ]
    )

    analyse   = phase_analyse(build_ctx(sources), stats)
    score     = analyse.get("score_actuel", 35)
    niveau    = analyse.get("niveau_os", "?")
    plan      = analyse.get("plan_ameliorations", [])
    milestone = analyse.get("prochaine_milestone", "?")
    features  = analyse.get("fonctionnalites_presentes", [])
    manques   = analyse.get("fonctionnalites_manquantes_critiques", [])

    order = {"CRITIQUE": 0, "HAUTE": 1, "NORMALE": 2, "BASSE": 3}
    plan  = sorted(plan, key=lambda t: (order.get(t.get("priorite", "NORMALE"), 2), t.get("nom", "")))

    log(f"Score={score}/100 | {niveau} | {len(plan)} tâche(s) planifiées", "STAT")

    if milestone:
        if milestone not in ms_cache:
            ms_num = gh_ensure_milestone(milestone, f"Objectif: {milestone}")
            if ms_num:
                ms_cache[milestone] = ms_num
                log(f"Milestone '{milestone}' = #{ms_num}")

    disc_now(
        f"📊 Analyse: {score}/100 — {niveau}",
        f"```\n{pbar(score)}\n```",
        0x00AAFF if score >= 60 else 0xFFA500 if score >= 30 else 0xFF4444,
        [
            {"name": "✅ Présentes",
             "value": "\n".join(f"+ {f}" for f in features[:6]) or "—",
             "inline": True},
            {"name": "❌ Manquantes",
             "value": "\n".join(f"- {f}" for f in manques[:6]) or "—",
             "inline": True},
            {"name": "📋 Plan",
             "value": "\n".join(
                 f"[{i+1}] `{t.get('priorite','?')[:3]}` {t.get('nom','?')[:38]}"
                 for i, t in enumerate(plan[:8])
             ) or "—",
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
            log(f"Watchdog: arrêt avant tâche {i}/{total}", "WARN")
            break

        if remaining_time() < 180:
            log(f"Moins de 3 minutes restantes — arrêt propre avant tâche {i}/{total}", "WARN")
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

            ms_title = task.get("milestone", milestone)
            if ms_title and ms_title in ms_cache:
                for written_file in (written or []):
                    pass
        else:
            tasks_failed.append(task.get("nom", "?"))

        if i < total and watchdog():
            n_al  = len(alive())
            pause = 3 if n_al >= 5 else 6 if n_al >= 3 else 12 if n_al >= 1 else 20
            log(f"Pause {pause}s ({n_al} provider(s) dispo, {int(remaining_time())}s restants)")
            _flush_disc(True)
            time.sleep(pause)

    log(f"\n{'='*56}\nCYCLE TERMINÉ: {success}/{total} tâches réussies\n{'='*56}")

    if success > 0:
        log("[Release] Création de la release GitHub...")
        sf = read_all(force=True)
        create_release(tasks_done, tasks_failed, analyse, proj_stats(sf))
    else:
        log("[Release] Aucun succès — pas de release créée")

    sf = read_all(force=True)
    final_report(success, total, tasks_done, tasks_failed, analyse, proj_stats(sf))
    _flush_disc(True)

    print(f"\n{'='*64}")
    print(f"[FIN] {success}/{total} | uptime: {uptime()} | GH RL: {GH_RATE['remaining']}")
    print(f"      Providers: {prov_summary().split(' — ')[0] if ' — ' in prov_summary() else prov_summary()}")
    print(f"      IA calls: {_CYCLE_STATS.get('ai_calls',0)} | 429: {_CYCLE_STATS.get('total_429',0)} | tokens: ~{sum(p['tokens'] for p in PROVIDERS):,}")
    for t in tasks_done:
        fc = t.get("fix_count", 0)
        print(f"  ✅ {t.get('nom','?')[:58]} ({t.get('elapsed',0):.0f}s){' fix×'+str(fc) if fc else ''}")
    for n in tasks_failed:
        print(f"  ❌ {n[:58]}")
    print("=" * 64)

if __name__ == "__main__":
    main()
