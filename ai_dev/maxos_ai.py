#!/usr/bin/env python3
"""MaxOS AI Developer v16.1 — os.img garanti, build fail silent corrigé"""

import os, sys, json, time, subprocess, re, hashlib, traceback, random, socket, atexit
import urllib.request, urllib.error, urllib.parse
from datetime import datetime, timezone
from collections import defaultdict, deque

VERSION     = "16.1"
DEBUG       = os.environ.get("MAXOS_DEBUG", "0") == "1"
START_TIME  = time.time()
MAX_RUNTIME = 3300

REPO_OWNER = os.environ.get("REPO_OWNER", "MaxLananas")
REPO_NAME  = os.environ.get("REPO_NAME",  "MaxOS")
REPO_PATH  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GH_TOKEN   = os.environ.get("GH_PAT", "") or os.environ.get("GITHUB_TOKEN", "")
DISCORD_WH = os.environ.get("DISCORD_WEBHOOK", "")

# ── MODELS ────────────────────────────────────────────────────────────────────
GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

OPENROUTER_MODELS = [
    "mistralai/devstral-small:free",
    "tngtech/deepseek-r1t-chimera:free",
    "deepseek/deepseek-chat-v3-0324:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.5-flash-preview-05-20",
]

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "moonshotai/kimi-k2-instruct",
]

MISTRAL_MODELS = [
    "mistral-small-latest",
    "mistral-medium-latest",
    "open-mixtral-8x7b",
]

# ── GLOBAL STATE ──────────────────────────────────────────────────────────────
GH_RATE      = {"remaining": 5000, "reset": 0}
SOURCE_CACHE = {"hash": None, "data": None}
TASK_METRICS = []
_DISC_BUF    = []
_DISC_LAST   = 0.0
_DISC_INTV   = 15
_CYCLE_STATS = defaultdict(int)

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

ICONS = {
    "INFO":"📋","WARN":"⚠️ ","ERROR":"❌","OK":"✅",
    "BUILD":"🔨","GIT":"📦","TIME":"⏱️ ","AI":"🤖","STAT":"📊",
}

def log(msg, level="INFO"):
    print(f"[{ts()}] {ICONS.get(level,'📋')} {msg}", flush=True)

def watchdog():
    elapsed = time.time() - START_TIME
    if elapsed >= MAX_RUNTIME:
        log(f"Watchdog: {int(elapsed)}s/{MAX_RUNTIME}s", "WARN")
        disc_now("⏰ Watchdog", f"Arrêt après **{uptime()}**", 0xFFA500)
        return False
    return True

# ── PROVIDERS ─────────────────────────────────────────────────────────────────
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

    result  = []
    max_len = max((len(p) for p in pools), default=0)
    for i in range(max_len):
        for pool in pools:
            if i < len(pool):
                result.append(pool[i])
    return result

PROVIDERS = load_providers()

def alive():
    now = time.time()
    al  = [p for p in PROVIDERS if not p["dead"] and now >= p["cooldown"]]
    al.sort(key=lambda p: (p["consec_429"]*5 + p["errors"]*2, -p["success_rate"]))
    return al

def non_dead():
    return [p for p in PROVIDERS if not p["dead"]]

def avg_rt(p):
    rt = p.get("response_times",[])
    return sum(rt)/len(rt) if rt else 999.0

def prov_summary():
    now = time.time()
    by  = defaultdict(lambda: [0,0,0])
    for p in PROVIDERS:
        t = p["type"]
        if p["dead"]:             by[t][2] += 1
        elif now >= p["cooldown"]:by[t][0] += 1
        else:                     by[t][1] += 1
    parts = [f"**{t}**: 🟢{v[0]} 🟡{v[1]} 💀{v[2]}" for t,v in sorted(by.items())]
    return f"{len(alive())}/{len(non_dead())} dispo — " + " | ".join(parts)

def _propagate_key_dead(key_prefix):
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
        _CYCLE_STATS["providers_dead"] += 1
        log(f"Provider {p['id']} → MORT", "ERROR")
        return
    p["errors"]      += 1
    p["consec_429"]  += 1
    p["success_rate"] = max(0.0, p["success_rate"] - 0.15)
    if secs is None:
        secs = min(15*(2**min(p["errors"]-1,4)) + random.uniform(0,3), 180)
    p["cooldown"] = time.time() + secs
    log(f"Provider {p['id']} → cooldown {int(secs)}s (errs={p['errors']})", "WARN")

def reward(p, elapsed):
    p["errors"]      = max(0, p["errors"]-1)
    p["consec_429"]  = 0
    p["last_ok"]     = time.time()
    p["success_rate"]= min(1.0, p["success_rate"]+0.05)
    p["response_times"].append(elapsed)
    _CYCLE_STATS["total_calls"] += 1

def pick():
    al = alive()
    if al:
        chosen = al[0]
        if DEBUG: log(f"  pick → {chosen['id']} sr={chosen['success_rate']:.2f}", "INFO")
        return chosen
    nd = non_dead()
    if not nd:
        log("FATAL: tous les providers sont morts", "ERROR")
        disc_now("💀 Mort totale", "Arrêt.", 0xFF0000)
        sys.exit(1)
    best = min(nd, key=lambda p: p["cooldown"])
    wait = min(max(best["cooldown"] - time.time() + 0.5, 0.5), 90)
    log(f"Tous en cooldown → attente {int(wait)}s → {best['id']}", "TIME")
    _CYCLE_STATS["total_waits"] += 1
    time.sleep(wait)
    return best

# ── API CALLS ─────────────────────────────────────────────────────────────────
def _call_gemini(p, prompt, max_tok, timeout):
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tok, "temperature": 0.05, "candidateCount": 1},
    }).encode("utf-8")
    req = urllib.request.Request(p["url"], data=payload,
                                  headers={"Content-Type":"application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode("utf-8"))
    cands = data.get("candidates",[])
    if not cands: return None
    c = cands[0]
    if c.get("finishReason","") in ("SAFETY","RECITATION","PROHIBITED_CONTENT"): return None
    parts = c.get("content",{}).get("parts",[])
    texts = [pt.get("text","") for pt in parts
             if isinstance(pt,dict) and not pt.get("thought") and pt.get("text")]
    result = "".join(texts).strip()
    return result if result else None

def _call_compat(p, prompt, max_tok, timeout):
    limits = {"groq":26000,"openrouter":45000,"mistral":50000}
    lim = limits.get(p["type"],50000)
    if len(prompt) > lim: prompt = prompt[:lim] + "\n[TRONQUÉ]"
    if p["type"] == "groq": max_tok = min(max_tok,8000)

    payload = json.dumps({
        "model": p["model"], "messages": [{"role":"user","content":prompt}],
        "max_tokens": max_tok, "temperature": 0.05,
    }).encode("utf-8")
    headers = {"Content-Type":"application/json", "Authorization":f"Bearer {p['key']}"}
    if p["type"] == "openrouter":
        headers["HTTP-Referer"] = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
        headers["X-Title"]      = f"MaxOS AI v{VERSION}"

    req = urllib.request.Request(p["url"], data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode("utf-8"))
    if "error" in data: raise RuntimeError(data["error"].get("message","unknown")[:250])
    choices = data.get("choices",[])
    if not choices: return None
    content = choices[0].get("message",{}).get("content","")
    return content.strip() if content else None

def ai_call(prompt, max_tokens=32768, timeout=160, tag="?"):
    if len(prompt) > 54000: prompt = prompt[:54000] + "\n[TRONQUÉ]"
    max_att    = min(len(PROVIDERS)*2, 30)
    last_error = "aucune tentative"
    _CYCLE_STATS["ai_calls"] += 1

    for attempt in range(1, max_att+1):
        if not watchdog(): return None
        p  = pick()
        t0 = time.time()
        log(f"[{tag}] {p['type']}/{p['id']} att={attempt} sr={p['success_rate']:.2f}", "AI")
        try:
            text = _call_gemini(p,prompt,max_tokens,timeout) if p["type"]=="gemini" \
                   else _call_compat(p,prompt,max_tokens,timeout)
            elapsed = round(time.time()-t0,1)
            if not text or not text.strip():
                log(f"[{tag}] Réponse vide ({p['id']}) {elapsed}s","WARN")
                penalize(p,12); continue
            p["calls"]  += 1
            p["tokens"] += len(text)//4
            reward(p,elapsed)
            _CYCLE_STATS["total_tokens"] += len(text)//4
            log(f"[{tag}] ✅ {len(text):,}c {elapsed}s ({p['type']}/{p['model'][:22]})","OK")
            return text

        except urllib.error.HTTPError as e:
            elapsed = round(time.time()-t0,1)
            body = ""
            try: body = e.read().decode("utf-8",errors="replace")[:600]
            except: pass
            last_error = f"HTTP {e.code}"
            log(f"[{tag}] HTTP {e.code} ({p['id']}) {elapsed}s","WARN")
            if e.code == 429:
                _CYCLE_STATS["total_429"] += 1; penalize(p)
            elif e.code == 401:
                _propagate_key_dead(p["key_prefix"])
            elif e.code == 403:
                bl = body.lower()
                kill = ["denied","banned","suspended","not authorized","forbidden","deactivated","invalid api key"]
                if any(w in bl for w in kill): _propagate_key_dead(p["key_prefix"])
                else: penalize(p,180)
            elif e.code == 404:
                penalize(p,dead=True)
            elif e.code == 400:
                if "not a valid model" in body.lower() or "no endpoints found" in body.lower():
                    penalize(p,dead=True)
                else: penalize(p,40)
            elif e.code in (500,502,503,504): penalize(p,20); time.sleep(2)
            elif e.code == 408: penalize(p,25)
            else: penalize(p,15); time.sleep(1)

        except (TimeoutError, socket.timeout):
            log(f"[{tag}] TIMEOUT {timeout}s ({p['id']})","WARN")
            penalize(p,30)
        except urllib.error.URLError as e:
            log(f"[{tag}] URLError ({p['id']}): {e.reason}","WARN")
            penalize(p,18); time.sleep(2)
        except RuntimeError as e:
            log(f"[{tag}] RuntimeError ({p['id']}): {e}","WARN")
            penalize(p,22)
        except json.JSONDecodeError as e:
            log(f"[{tag}] JSON error ({p['id']}): {e}","WARN")
            penalize(p,10)
        except Exception as e:
            log(f"[{tag}] Exception ({p['id']}): {type(e).__name__}: {e}","ERROR")
            if DEBUG: traceback.print_exc()
            penalize(p,12); time.sleep(1)

    _CYCLE_STATS["ai_failures"] += 1
    log(f"[{tag}] ÉCHEC TOTAL {max_att} att. Dernière: {last_error}","ERROR")
    return None

# ── DISCORD ───────────────────────────────────────────────────────────────────
def _disc_raw(embeds):
    if not DISCORD_WH: return False
    payload = json.dumps({"username":f"MaxOS AI v{VERSION}","embeds":embeds[:10]}).encode()
    req = urllib.request.Request(DISCORD_WH, data=payload,
                                  headers={"Content-Type":"application/json","User-Agent":f"MaxOS-Bot/{VERSION}"},
                                  method="POST")
    try:
        with urllib.request.urlopen(req,timeout=10) as r: return r.status in (200,204)
    except Exception as ex:
        if DEBUG: log(f"Discord err: {ex}","WARN")
        return False

def _make_embed(title, desc, color, fields=None):
    al  = len(alive()); nd = len(non_dead())
    tk  = sum(p["tokens"] for p in PROVIDERS)
    ca  = sum(p["calls"]  for p in PROVIDERS)
    cur = alive()[0]["model"][:22] if alive() else "aucun"
    e   = {
        "title":       str(title)[:256],
        "description": str(desc)[:4096],
        "color":       color,
        "timestamp":   datetime.utcnow().isoformat()+"Z",
        "footer":      {"text":f"v{VERSION} | {cur} | {al}/{nd} | up {uptime()} | ~{tk:,}tk | {ca}c"},
    }
    if fields:
        e["fields"] = [
            {"name":str(f.get("name","?"))[:256],"value":str(f.get("value","?"))[:1024],"inline":bool(f.get("inline",False))}
            for f in fields[:25] if f.get("value") and str(f.get("value","")).strip()
        ]
    return e

def disc_log(title, desc="", color=0x5865F2):
    _DISC_BUF.append((title,desc,color))
    _flush_disc(False)

def _flush_disc(force=True):
    global _DISC_LAST
    now = time.time()
    if not force and now - _DISC_LAST < _DISC_INTV: return
    while len(_DISC_BUF) > 50: _DISC_BUF.pop(0)
    if not _DISC_BUF: return
    embeds = []
    while _DISC_BUF and len(embeds) < 10:
        t,d,c = _DISC_BUF.pop(0)
        embeds.append(_make_embed(t,d,c))
    if embeds: _disc_raw(embeds); _DISC_LAST = time.time()

def disc_now(title, desc="", color=0x5865F2, fields=None):
    _flush_disc(True)
    _disc_raw([_make_embed(title,desc,color,fields)])

atexit.register(_flush_disc,True)

# ── GITHUB API ────────────────────────────────────────────────────────────────
def gh_api(method, endpoint, data=None, raw_url=None, retry=3, silent=False):
    if not GH_TOKEN: return None
    url     = raw_url or f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/{endpoint}"
    payload = json.dumps(data).encode() if data else None
    for att in range(1, retry+1):
        req = urllib.request.Request(url, data=payload, headers={
            "Authorization":f"Bearer {GH_TOKEN}","Accept":"application/vnd.github+json",
            "Content-Type":"application/json","User-Agent":f"MaxOS-AI/{VERSION}",
            "X-GitHub-Api-Version":"2022-11-28",
        }, method=method)
        try:
            with urllib.request.urlopen(req,timeout=30) as r:
                rem=r.headers.get("X-RateLimit-Remaining"); rst=r.headers.get("X-RateLimit-Reset")
                if rem: GH_RATE["remaining"]=int(rem)
                if rst: GH_RATE["reset"]=int(rst)
                if GH_RATE["remaining"]<80: log(f"GH rate limit: {GH_RATE['remaining']} restants!","WARN")
                raw=r.read().decode("utf-8",errors="replace")
                return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as e:
            body=""
            try: body=e.read().decode("utf-8",errors="replace")[:400]
            except: pass
            if e.code==403 and "rate limit" in body.lower():
                wait=max(GH_RATE["reset"]-time.time()+5,60)
                log(f"GH rate limit → attente {int(wait)}s","WARN"); time.sleep(wait); continue
            if e.code in (500,502,503,504) and att<retry: time.sleep(5*att); continue
            if not silent: log(f"GH {method} {endpoint[:60]} HTTP {e.code}: {body[:120]}","WARN")
            return None
        except Exception as ex:
            if att<retry: time.sleep(3); continue
            if not silent: log(f"GH ex: {ex}","ERROR")
            return None
    return None

def gh_open_prs():
    r=gh_api("GET","pulls?state=open&per_page=20&sort=updated&direction=desc")
    return r if isinstance(r,list) else []

def gh_pr_files(n):
    r=gh_api("GET",f"pulls/{n}/files?per_page=50")
    return r if isinstance(r,list) else []

def gh_pr_reviews(n):
    r=gh_api("GET",f"pulls/{n}/reviews")
    return r if isinstance(r,list) else []

def gh_post_review(n,body,event="COMMENT",comments=None):
    pay={"body":body,"event":event}
    if comments: pay["comments"]=[{"path":c["path"],"line":c.get("line",1),"side":"RIGHT","body":c["body"]} for c in comments if c.get("path") and c.get("body")]
    return gh_api("POST",f"pulls/{n}/reviews",pay)

def gh_approve_pr(n,body):   return gh_post_review(n,body,"APPROVE")
def gh_req_changes(n,body,comments=None): return gh_post_review(n,body,"REQUEST_CHANGES",comments)

def gh_open_issues():
    r=gh_api("GET","issues?state=open&per_page=30&sort=updated&direction=desc")
    if not isinstance(r,list): return []
    return [i for i in r if not i.get("pull_request")]

def gh_issue_comments(n):
    r=gh_api("GET",f"issues/{n}/comments?per_page=50")
    return r if isinstance(r,list) else []

def gh_close_issue(n,reason="completed"):
    gh_api("PATCH",f"issues/{n}",{"state":"closed","state_reason":reason})

def gh_add_labels(n,labels):
    if labels: gh_api("POST",f"issues/{n}/labels",{"labels":labels})

def gh_post_comment(n,body):
    gh_api("POST",f"issues/{n}/comments",{"body":body})

def gh_list_labels():
    r=gh_api("GET","labels?per_page=100")
    return {l["name"]:l for l in (r if isinstance(r,list) else [])}

def gh_ensure_labels(desired):
    ex=gh_list_labels(); created=0
    for name,color in desired.items():
        if name not in ex:
            gh_api("POST","labels",{"name":name,"color":color,"description":f"[MaxOS AI] {name}"})
            created+=1
    if created: log(f"Labels: {created} créé(s)")

STANDARD_LABELS = {
    "ai-reviewed":"0075ca","ai-approved":"0e8a16","ai-rejected":"b60205",
    "ai-generated":"8b5cf6","needs-fix":"e4e669","bug":"d73a4a",
    "enhancement":"a2eeef","stale":"eeeeee","kernel":"5319e7",
    "driver":"1d76db","app":"0052cc","boot":"e11d48","security":"b91c1c",
}

def gh_ensure_milestone(title,description=""):
    r=gh_api("GET","milestones?state=open&per_page=30")
    for m in (r if isinstance(r,list) else []):
        if m.get("title")==title: return m.get("number")
    r2=gh_api("POST","milestones",{"title":title,"description":description or f"[AI] {title}"})
    return r2.get("number") if r2 else None

def gh_list_releases(n=10):
    r=gh_api("GET",f"releases?per_page={n}")
    return r if isinstance(r,list) else []

def gh_create_release(tag, name, body, pre=False):
    r=gh_api("POST","releases",{
        "tag_name":tag,"target_commitish":"main",
        "name":name,"body":body,"draft":False,"prerelease":pre,
    })
    return r if r else None

def gh_upload_asset(release_id, filepath, name):
    """Upload un fichier comme asset d'une release GitHub."""
    if not GH_TOKEN or not os.path.exists(filepath): return None
    url = f"https://uploads.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/{release_id}/assets?name={name}"
    size = os.path.getsize(filepath)
    log(f"Upload asset: {name} ({size} bytes) → release {release_id}")
    try:
        with open(filepath,"rb") as f:
            data = f.read()
        req = urllib.request.Request(url, data=data, headers={
            "Authorization":f"Bearer {GH_TOKEN}",
            "Content-Type":"application/octet-stream",
            "User-Agent":f"MaxOS-AI/{VERSION}",
        }, method="POST")
        with urllib.request.urlopen(req,timeout=60) as r:
            resp = json.loads(r.read().decode("utf-8",errors="replace"))
            url_dl = resp.get("browser_download_url","?")
            log(f"Asset uploadé: {url_dl}","OK")
            return url_dl
    except Exception as ex:
        log(f"Upload asset erreur: {ex}","ERROR")
        return None

def gh_repo_info():
    repo=gh_api("GET","") or {}; langs=gh_api("GET","languages") or {}
    return {"stars":repo.get("stargazers_count",0),"forks":repo.get("forks_count",0),
            "size_kb":repo.get("size",0),"languages":langs}

def gh_compare(base,head):
    r=gh_api("GET",f"compare/{base}...{head}")
    return r if isinstance(r,dict) else {}

# ── GIT ───────────────────────────────────────────────────────────────────────
def git_cmd(args,timeout=60):
    try:
        r=subprocess.run(["git"]+args,cwd=REPO_PATH,capture_output=True,text=True,timeout=timeout)
        return r.returncode==0,r.stdout,r.stderr
    except subprocess.TimeoutExpired: return False,"",f"timeout {timeout}s"
    except Exception as e: return False,"",str(e)

def git_sha(short=True):
    ok,out,_=git_cmd(["rev-parse","HEAD"])
    if not ok: return ""
    s=out.strip(); return s[:7] if short else s

def git_current_branch():
    ok,out,_=git_cmd(["branch","--show-current"])
    return out.strip() if ok else "main"

def git_push(task_name, files, desc, model):
    if not files: return True,None,None
    dirs=set(f.split("/")[0] for f in files if "/" in f)
    pmap={"kernel":"kernel","drivers":"driver","boot":"boot","ui":"ui","apps":"feat"}
    prefix=next((pmap[d] for d in pmap if d in dirs),"feat")
    fshort=", ".join(os.path.basename(f) for f in files[:3])
    if len(files)>3: fshort+=f" +{len(files)-3}"
    short=f"{prefix}: {task_name[:50]} [{fshort}]"
    body=f"{short}\n\nFiles: {', '.join(files[:10])}\nModel: {model}\nArch: x86-32 bare metal\n\n[skip ci]"
    git_cmd(["add","-A"])
    ok,out,err=git_cmd(["commit","-m",body])
    if not ok:
        if "nothing to commit" in (out+err): log("Git: rien à committer"); return True,None,None
        log(f"Commit KO: {err[:250]}","ERROR"); return False,None,None
    sha=git_sha()
    ok2,_,e2=git_cmd(["push","--set-upstream","origin",git_current_branch()])
    if not ok2:
        git_cmd(["pull","--rebase","--autostash"])
        ok2,_,e2=git_cmd(["push"])
        if not ok2: log(f"Push KO: {e2[:250]}","ERROR"); return False,None,None
    _CYCLE_STATS["total_commits"]+=1
    log(f"Push OK: {sha} — {short[:60]}","GIT")
    return True,sha,short

# ── BUILD ─────────────────────────────────────────────────────────────────────
_ERR_RE = re.compile(
    r"(?:error:|fatal error:|fatal:|undefined reference|cannot find|no such file"
    r"|\*\*\* \[|nasm:.*error|ld:.*error|collect2: error|linker command failed"
    r"|multiple definition|duplicate symbol|identifier expected|undefined symbol)",
    re.IGNORECASE
)

def parse_errs(log_text):
    """Parse les erreurs de build. Détecte aussi les builds silencieux."""
    seen,result=[],[]
    for line in log_text.split("\n"):
        s=line.strip()
        if s and _ERR_RE.search(s) and s not in seen:
            seen.append(s); result.append(s[:140])
    return result[:35]

def _detect_silent_fail(log_text, returncode):
    """
    Détecte un build qui échoue sans message d'erreur parsable.
    Retourne une description du problème ou None si pas de problème silencieux.
    """
    if returncode == 0: return None
    lines = log_text.split("\n")
    # Cherche "Error N" en fin de ligne make
    for line in lines:
        s = line.strip()
        if re.search(r"Error \d+", s) or "FAILED" in s:
            return s[:140]
        if "make[" in s and "Error" in s:
            return s[:140]
        if "*** " in s:
            return s[:140]
    # Retourne les dernières lignes non-vides comme indice
    non_empty = [l.strip() for l in lines if l.strip()]
    if non_empty:
        return f"Build fail silencieux. Dernières lignes: {' | '.join(non_empty[-3:])}"
    return "Build fail sans sortie"

def make_build():
    """Build complet avec make clean. Détecte les fails silencieux."""
    subprocess.run(["make","clean"], cwd=REPO_PATH, capture_output=True, timeout=30)

    # S'assurer que le dossier build existe
    build_dir = os.path.join(REPO_PATH, "build")
    os.makedirs(build_dir, exist_ok=True)

    t0 = time.time()
    try:
        r = subprocess.run(["make","-j2"], cwd=REPO_PATH,
                            capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        log("Build TIMEOUT 180s","ERROR")
        return False,"TIMEOUT",["Build timeout après 180s"]

    el   = round(time.time()-t0,1)
    lt   = r.stdout + r.stderr
    errs = parse_errs(lt)

    if r.returncode == 0:
        # Vérifier que os.img a bien été créé
        img_path = os.path.join(REPO_PATH,"os.img")
        if not os.path.exists(img_path):
            # make a réussi mais os.img absent — créer manuellement
            log("make OK mais os.img absent — création manuelle","WARN")
            boot_bin   = os.path.join(build_dir,"boot.bin")
            kernel_bin = os.path.join(build_dir,"kernel.bin")
            if os.path.exists(boot_bin):
                _create_osimg(boot_bin, kernel_bin if os.path.exists(kernel_bin) else None)
        _CYCLE_STATS["builds_ok"]+=1
        log(f"Build OK {el}s","BUILD")
        disc_log("🔨 Build ✅",f"`{el}s`",0x00CC44)
        return True,lt,[]

    # Build échoué
    if not errs:
        # Fail silencieux — extraire plus d'info
        silent_desc = _detect_silent_fail(lt, r.returncode)
        if silent_desc:
            errs = [silent_desc]
            log(f"Build FAIL silencieux: {silent_desc[:80]}","BUILD")
        else:
            errs = [f"make retourné {r.returncode} sans erreur parsable"]
            log(f"Build FAIL rc={r.returncode} sans erreur parsable","BUILD")
    else:
        log(f"Build FAIL ({len(errs)} err) {el}s","BUILD")

    for e in errs[:6]: log(f"  >> {e[:115]}","BUILD")
    _CYCLE_STATS["builds_fail"]+=1
    es="\n".join(f"`{e[:85]}`" for e in errs[:5])
    disc_log(f"🔨 Build ❌ ({len(errs)} err)",f"`{el}s`\n{es}",0xFF2200)
    return False,lt,errs

def _create_osimg(boot_bin, kernel_bin=None):
    """Crée os.img via dd."""
    img_path = os.path.join(REPO_PATH,"os.img")
    try:
        # Crée image vide 1.44MB
        subprocess.run(["dd","if=/dev/zero","of="+img_path,"bs=512","count=2880"],
                       cwd=REPO_PATH, capture_output=True, timeout=10)
        # Copie boot sector
        subprocess.run(["dd","if="+boot_bin,"of="+img_path,"conv=notrunc"],
                       cwd=REPO_PATH, capture_output=True, timeout=10)
        # Copie kernel si disponible
        if kernel_bin:
            subprocess.run(["dd","if="+kernel_bin,"of="+img_path,"seek=1","conv=notrunc"],
                           cwd=REPO_PATH, capture_output=True, timeout=10)
        size = os.path.getsize(img_path)
        log(f"os.img créé manuellement: {size} bytes","OK")
        return True
    except Exception as e:
        log(f"Erreur création os.img: {e}","ERROR")
        return False

def ensure_osimg():
    """S'assure que os.img existe après un build réussi."""
    img_path   = os.path.join(REPO_PATH,"os.img")
    build_dir  = os.path.join(REPO_PATH,"build")
    boot_bin   = os.path.join(build_dir,"boot.bin")
    kernel_bin = os.path.join(build_dir,"kernel.bin")

    if os.path.exists(img_path) and os.path.getsize(img_path) > 512:
        return True

    if os.path.exists(boot_bin):
        return _create_osimg(boot_bin, kernel_bin if os.path.exists(kernel_bin) else None)

    log("os.img et boot.bin absents — impossible de créer l'image","WARN")
    return False

# ── FILE DISCOVERY ────────────────────────────────────────────────────────────
SKIP_DIRS  = {".git","build","__pycache__",".github","ai_dev",".vscode","node_modules","docs","tests"}
SKIP_FILES = {".DS_Store","Thumbs.db"}
SRC_EXTS   = {".c",".h",".asm",".ld",".s"}

CANONICAL_FILES = [
    "boot/boot.asm","kernel/kernel_entry.asm","kernel/kernel.c",
    "kernel/io.h","kernel/idt.h","kernel/idt.c","kernel/isr.asm",
    "kernel/timer.h","kernel/timer.c","kernel/memory.h","kernel/memory.c",
    "drivers/screen.h","drivers/screen.c","drivers/keyboard.h","drivers/keyboard.c",
    "drivers/vga.h","drivers/vga.c","apps/terminal.h","apps/terminal.c",
    "Makefile","linker.ld",
]

def discover_files():
    found=[]
    for root,dirs,files in os.walk(REPO_PATH):
        dirs[:]=[d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f in SKIP_FILES: continue
            ext=os.path.splitext(f)[1]
            if ext in SRC_EXTS or f=="Makefile":
                rel=os.path.relpath(os.path.join(root,f),REPO_PATH).replace("\\","/")
                found.append(rel)
    return sorted(found)

def read_all(force=False):
    af=sorted(set(CANONICAL_FILES+discover_files()))
    h=hashlib.md5()
    for f in af:
        p=os.path.join(REPO_PATH,f)
        if os.path.exists(p):
            try:
                st=os.stat(p); h.update(f"{f}:{st.st_mtime:.3f}:{st.st_size}".encode())
            except: pass
    cur=h.hexdigest()
    if not force and SOURCE_CACHE["hash"]==cur and SOURCE_CACHE["data"]:
        return SOURCE_CACHE["data"]
    src={}
    for f in af:
        p=os.path.join(REPO_PATH,f)
        if os.path.exists(p):
            try:
                with open(p,"r",encoding="utf-8",errors="ignore") as fh: src[f]=fh.read()
            except: src[f]=None
        else: src[f]=None
    SOURCE_CACHE["hash"]=cur; SOURCE_CACHE["data"]=src
    return src

def proj_stats(sources):
    files=sum(1 for c in sources.values() if c)
    lines=sum(c.count("\n") for c in sources.values() if c)
    chars=sum(len(c) for c in sources.values() if c)
    by_ext=defaultdict(int)
    for f,c in sources.items():
        if c: ext=os.path.splitext(f)[1] or "other"; by_ext[ext]+=1
    return {"files":files,"lines":lines,"chars":chars,"by_ext":dict(by_ext)}

def build_ctx(sources, max_chars=38000):
    lines=["=== CODE SOURCE MAXOS ===\n\nFICHIERS PRÉSENTS:\n"]
    for f,c in sources.items():
        lines.append(f"  {'✅' if c else '❌'} {f} ({len(c) if c else 0} chars)\n")
    lines.append("\n"); ctx="".join(lines); used=len(ctx)
    prio=["kernel/kernel.c","kernel/kernel_entry.asm","kernel/io.h","Makefile","linker.ld",
          "drivers/screen.h","drivers/keyboard.h"]
    done=set()
    for f in prio:
        c=sources.get(f,"")
        if not c: continue
        block=f"{'='*50}\nFICHIER: {f}\n{'='*50}\n{c}\n\n"
        if used+len(block)>max_chars: ctx+=f"[{f}: {len(c)} chars — tronqué]\n"; done.add(f); continue
        ctx+=block; used+=len(block); done.add(f)
    for f,c in sources.items():
        if f in done or not c: continue
        block=f"{'='*50}\nFICHIER: {f}\n{'='*50}\n{c}\n\n"
        if used+len(block)>max_chars: ctx+=f"[{f}: {len(c)} chars — tronqué]\n"; continue
        ctx+=block; used+=len(block)
    return ctx

def analyze_quality(sources):
    bad_inc=["stddef.h","string.h","stdlib.h","stdio.h","stdint.h","stdbool.h","stdarg.h"]
    bad_sym=["size_t","NULL","bool","true","false","uint32_t","uint8_t","uint16_t","int32_t",
             "malloc","free","calloc","realloc","memset","memcpy","memmove",
             "strlen","strcpy","strcat","printf","sprintf","puts"]
    violations=[]; cf=af=0
    for fname,content in sources.items():
        if not content: continue
        if fname.endswith((".c",".h")):
            cf+=1
            for i,line in enumerate(content.split("\n"),1):
                s=line.strip()
                if s.startswith(("//","/*","*","#pragma")): continue
                for inc in bad_inc:
                    if f"#include <{inc}>" in line or f'#include "{inc}"' in line:
                        violations.append(f"{fname}:{i} [INC] {inc}")
                for sym in bad_sym:
                    if re.search(r"\b"+re.escape(sym)+r"\b",line):
                        violations.append(f"{fname}:{i} [SYM] {sym}"); break
        elif fname.endswith((".asm",".s")): af+=1
    score=max(0,100-len(violations)*3)
    return {"score":score,"violations":violations[:35],"c_files":cf,"asm_files":af}

# ── FILE PARSING ──────────────────────────────────────────────────────────────
FILE_START_RE = re.compile(
    r"(?:={3,}|-{3,})\s*FILE\s*:\s*[`'\"]?([A-Za-z0-9_./@-][A-Za-z0-9_./@ -]*?)[`'\"]?\s*(?:={3,}|-{3,})",
    re.IGNORECASE)
FILE_END_RE    = re.compile(r"(?:={3,}|-{3,})\s*END\s*(?:FILE)?\s*(?:={3,}|-{3,})",re.IGNORECASE)
FILE_DELETE_RE = re.compile(
    r"(?:={3,}|-{3,})\s*DELETE\s*:\s*[`'\"]?([A-Za-z0-9_./@-][A-Za-z0-9_./@ -]*?)[`'\"]?\s*(?:={3,}|-{3,})",
    re.IGNORECASE)

def parse_ai_files(resp):
    files={};to_del=[];cur=None;lines=[];in_f=False
    for raw_line in resp.split("\n"):
        s=raw_line.strip()
        del_m=FILE_DELETE_RE.match(s)
        if del_m:
            fn=del_m.group(1).strip()
            if fn: to_del.append(fn)
            continue
        start_m=FILE_START_RE.match(s)
        if start_m:
            if in_f and cur and lines: _commit_file(files,cur,lines)
            fn=start_m.group(1).strip()
            if fn and not fn.startswith("-") and len(fn)>1: cur=fn;lines=[];in_f=True
            continue
        if FILE_END_RE.match(s) and in_f:
            if cur and lines: _commit_file(files,cur,lines)
            cur=None;lines=[];in_f=False; continue
        if in_f: lines.append(raw_line)
    if in_f and cur and lines: _commit_file(files,cur,lines)
    if not files and not to_del: log(f"Parse: aucun fichier. Début: {resp[:200]}","WARN")
    return files,to_del

def _commit_file(files_dict,path,lines):
    path=path.strip().strip("`'\"")
    content="\n".join(lines).strip()
    for fence in ("```c","```asm","```nasm","```makefile","```ld","```bash","```text","```"):
        if content.startswith(fence): content=content[len(fence):].lstrip("\n"); break
    if content.endswith("```"): content=content[:-3].rstrip("\n")
    content=content.strip()
    if content and len(content)>5:
        files_dict[path]=content
        log(f"Parsé: {path} ({len(content):,}c)")
    else: log(f"Parsé vide ignoré: {path}","WARN")

def write_files(files):
    written=[]; repo_real=os.path.realpath(REPO_PATH)+os.sep
    for path,content in files.items():
        path=path.strip().strip("/").replace("\\","/")
        full=os.path.realpath(os.path.join(REPO_PATH,path))
        if not (full+os.sep).startswith(repo_real):
            log(f"Path traversal bloqué: {path}","ERROR"); continue
        if not content or len(content)<5:
            log(f"Contenu trop court ignoré: {path}","WARN"); continue
        parent=os.path.dirname(full)
        if parent and parent!=REPO_PATH: os.makedirs(parent,exist_ok=True)
        try:
            with open(full,"w",encoding="utf-8",newline="\n") as f: f.write(content)
            written.append(path)
            log(f"Écrit: {path} ({len(content):,}c)")
        except Exception as e: log(f"Erreur écriture {path}: {e}","ERROR")
    SOURCE_CACHE["hash"]=None
    return written

def del_files(paths):
    deleted=[]; repo_real=os.path.realpath(REPO_PATH)+os.sep
    for path in paths:
        path=path.strip().strip("/")
        full=os.path.realpath(os.path.join(REPO_PATH,path))
        if not (full+os.sep).startswith(repo_real):
            log(f"Delete traversal bloqué: {path}","ERROR"); continue
        if os.path.exists(full) and os.path.isfile(full):
            os.remove(full); deleted.append(path); log(f"Supprimé: {path}")
    SOURCE_CACHE["hash"]=None
    return deleted

def backup(paths):
    bak={}
    for p in paths:
        full=os.path.join(REPO_PATH,p)
        if os.path.exists(full) and os.path.isfile(full):
            try:
                with open(full,"r",encoding="utf-8",errors="ignore") as f: bak[p]=f.read()
            except: pass
    return bak

def restore(bak):
    if not bak: return
    for p,c in bak.items():
        full=os.path.join(REPO_PATH,p); parent=os.path.dirname(full)
        if parent: os.makedirs(parent,exist_ok=True)
        try:
            with open(full,"w",encoding="utf-8",newline="\n") as f: f.write(c)
        except Exception as e: log(f"Erreur restore {p}: {e}","ERROR")
    log(f"Restauré {len(bak)} fichier(s)")
    SOURCE_CACHE["hash"]=None

# ── OS CONSTANTS ──────────────────────────────────────────────────────────────
OS_MISSION=(
    "MISSION MaxOS: OS bare metal x86 complet, moderne, stable.\n"
    "PROGRESSION: Boot→IDT+PIC→Timer PIT→Mémoire bitmap→VGA→Clavier IRQ→Terminal→GUI"
)

RULES="""╔══ RÈGLES BARE METAL x86 — VIOLATIONS = ÉCHEC BUILD ══╗
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
║   • kernel/io.h: SEUL fichier avec outb/inb static    ║
║     inline — JAMAIS redéfinir ailleurs                 ║
║   • isr.asm: PAS de %macro/%rep pour les stubs ISR    ║
║     Écrire isr0:...isr47: MANUELLEMENT                 ║
║   • kernel_entry.asm: global _stack_top EN PREMIER     ║
║   • Tout .c nouveau → dans Makefile OBJS              ║
║   • ZÉRO commentaire dans le code généré              ║
║   • os.img DOIT être créé par: make → dd boot+kernel  ║
╚════════════════════════════════════════════════════════╝"""

# Makefile canonique qui GARANTIT os.img
CANONICAL_MAKEFILE = """\
AS     = nasm
CC     = gcc
LD     = ld
CFLAGS = -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie -Wall -O2 -I.
LFLAGS = -m elf_i386 -T linker.ld --oformat binary
BFLAGS = -f bin
EFLAGS = -f elf

BUILD  = build

SRCS_C = kernel/kernel.c kernel/idt.c kernel/timer.c kernel/memory.c \\
         drivers/screen.c drivers/keyboard.c drivers/vga.c \\
         apps/terminal.c apps/notepad.c apps/sysinfo.c apps/about.c

OBJS_C = $(patsubst %.c,$(BUILD)/%.o,$(notdir $(SRCS_C)))

VPATH = kernel drivers apps

.PHONY: all clean

all: os.img

$(BUILD):
\tmkdir -p $(BUILD)

$(BUILD)/boot.bin: boot/boot.asm | $(BUILD)
\t$(AS) $(BFLAGS) $< -o $@

$(BUILD)/kernel_entry.o: kernel/kernel_entry.asm | $(BUILD)
\t$(AS) $(EFLAGS) $< -o $@

$(BUILD)/isr.o: kernel/isr.asm | $(BUILD)
\t$(AS) $(EFLAGS) $< -o $@

$(BUILD)/%.o: %.c | $(BUILD)
\t$(CC) $(CFLAGS) -c $< -o $@

$(BUILD)/kernel.bin: $(BUILD)/kernel_entry.o $(BUILD)/isr.o $(OBJS_C) | $(BUILD)
\t$(LD) $(LFLAGS) $^ -o $@

os.img: $(BUILD)/boot.bin $(BUILD)/kernel.bin
\tdd if=/dev/zero    of=$@ bs=512 count=2880
\tdd if=$(BUILD)/boot.bin   of=$@ conv=notrunc
\tdd if=$(BUILD)/kernel.bin of=$@ seek=1 conv=notrunc

clean:
\trm -rf $(BUILD) os.img
"""

LINKER_LD = """\
ENTRY(kmain)
OUTPUT_FORMAT(binary)

SECTIONS
{
    . = 0x1000;
    .text : { *(.text) }
    .data : { *(.data) }
    .rodata : { *(.rodata) }
    .bss  : { *(.bss) *(COMMON) }
}
"""

def _ensure_build_system():
    """Garantit que Makefile et linker.ld sont corrects et créent os.img."""
    mf_path  = os.path.join(REPO_PATH,"Makefile")
    ld_path  = os.path.join(REPO_PATH,"linker.ld")
    modified = False

    # Vérifier Makefile
    mf_ok = False
    if os.path.exists(mf_path):
        with open(mf_path,"r") as f: mf_content = f.read()
        # Makefile valide s'il contient os.img ET dd ET kernel.bin
        if "os.img" in mf_content and "dd" in mf_content and "kernel.bin" in mf_content:
            mf_ok = True

    if not mf_ok:
        log("Makefile invalide ou absent — injection du Makefile canonique","WARN")
        with open(mf_path,"w",newline="\n") as f: f.write(CANONICAL_MAKEFILE)
        modified = True

    # Vérifier linker.ld
    if not os.path.exists(ld_path):
        log("linker.ld absent — création","WARN")
        with open(ld_path,"w",newline="\n") as f: f.write(LINKER_LD)
        modified = True

    if modified: SOURCE_CACHE["hash"]=None
    return modified

# ── JSON PARSING ──────────────────────────────────────────────────────────────
def _parse_json_robust(resp):
    if not resp: return None
    clean=resp.strip()
    if clean.startswith("```"):
        lines=clean.split("\n"); end=-1 if lines[-1].strip()=="```" else len(lines)
        clean="\n".join(lines[1:end]).strip()
    i=clean.find("{"); j=clean.rfind("}")+1
    if i<0 or j<=i: return None
    candidate=clean[i:j]
    try: return json.loads(candidate)
    except: pass
    fixed=re.sub(r',\s*([}\]])',r'\1',candidate)
    try: return json.loads(fixed)
    except: pass
    fixed2=re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])',r'\\\\',candidate)
    try: return json.loads(fixed2)
    except: return None

# ── DEFAULT PLAN ──────────────────────────────────────────────────────────────
def default_plan():
    return {
        "score_actuel":  35, "niveau_os": "Prototype bare metal",
        "fonctionnalites_presentes": ["Boot x86","VGA texte 80x25"],
        "fonctionnalites_manquantes_critiques": ["IDT+PIC","Timer","Mémoire"],
        "prochaine_milestone": "Kernel stable IDT+Timer+Memory",
        "plan_ameliorations": [
            {
                "nom":                  "Makefile canonique + os.img garanti",
                "priorite":             "CRITIQUE",
                "categorie":            "build",
                "fichiers_a_modifier":  ["Makefile","linker.ld"],
                "fichiers_a_creer":     [],
                "fichiers_a_supprimer": [],
                "description": (
                    "Makefile avec règle os.img: "
                    "dd if=/dev/zero of=os.img bs=512 count=2880; "
                    "dd if=build/boot.bin of=os.img conv=notrunc; "
                    "dd if=build/kernel.bin of=os.img seek=1 conv=notrunc. "
                    "CFLAGS: -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie -I. "
                    "LFLAGS: -m elf_i386 -T linker.ld --oformat binary "
                    "linker.ld: ENTRY(kmain) SECTIONS {. = 0x1000; .text .data .rodata .bss}"
                ),
                "impact_attendu": "os.img bootable généré à chaque make",
                "complexite":     "BASSE",
            },
            {
                "nom":                  "kernel/io.h + kernel/idt.c + kernel/isr.asm",
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
                    "kernel/idt.h: struct IDTEntry packed; struct IDTPtr packed; "
                    "void idt_init(void); void idt_set_gate(unsigned char,unsigned int,unsigned short,unsigned char); "
                    "extern void isr0(); ... extern void isr47(); "
                    "kernel/idt.c: remap PIC (0x20/0xA0), fill idt[0..47], lidt. "
                    "kernel/isr.asm: BITS 32. Écrire EXPLICITEMENT isr0:...isr47: un par un. "
                    "isr_common: pushad/push ds.../call isr_handler/pop.../popad/add esp,8/iret."
                ),
                "impact_attendu": "IDT fonctionnelle, pas de triple fault",
                "complexite":     "HAUTE",
            },
            {
                "nom":                  "Timer PIT + Mémoire bitmap + Clavier IRQ",
                "priorite":             "HAUTE",
                "categorie":            "kernel",
                "fichiers_a_modifier":  ["kernel/kernel.c","Makefile"],
                "fichiers_a_creer":     ["kernel/timer.h","kernel/timer.c","kernel/memory.h","kernel/memory.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "timer.c: volatile unsigned int g_ticks=0; irq0: g_ticks++; outb(0x20,0x20); "
                    "timer_init: PIT diviseur=11931, outb(0x43,0x36)... "
                    "idt_set_gate(32,irq0,0x08,0x8E); outb(0x21,inb(0x21)&~0x01); "
                    "memory.c: bitmap[MAX_PAGES/32]; mem_init/mem_alloc/mem_free."
                ),
                "impact_attendu": "Timer 100Hz + allocateur pages 4KB",
                "complexite":     "HAUTE",
            },
        ],
    }

# ── ANALYSE ───────────────────────────────────────────────────────────────────
def phase_analyse(context, stats):
    log("=== PHASE 1: ANALYSE PROJET ===")
    disc_now("🔍 Analyse en cours",
             f"`{stats['files']}` fichiers | `{stats['lines']:,}` lignes",0x5865F2)
    prompt=(
        f"Tu es un expert OS bare metal x86. Retourne UNIQUEMENT du JSON valide.\n\n"
        f"{RULES}\n\n{OS_MISSION}\n\n"
        f"CONTEXT:\n{context[:18000]}\n\n"
        f"STATS: {stats['files']} fichiers, {stats['lines']} lignes\n\n"
        "IMPORTANT: Commence directement par { sans aucun texte avant.\n"
        '{"score_actuel":35,"niveau_os":"desc","fonctionnalites_presentes":["f1"],'
        '"fonctionnalites_manquantes_critiques":["f2"],"prochaine_milestone":"m",'
        '"plan_ameliorations":[{"nom":"N","priorite":"CRITIQUE","categorie":"kernel",'
        '"fichiers_a_modifier":["f"],"fichiers_a_creer":["g"],"fichiers_a_supprimer":[],'
        '"description":"specs précises","impact_attendu":"r","complexite":"HAUTE"}]}'
    )
    resp=ai_call(prompt,max_tokens=3000,timeout=70,tag="analyse")
    if not resp: log("Analyse IA indisponible → plan défaut","WARN"); return default_plan()
    result=_parse_json_robust(resp)
    if result and isinstance(result.get("plan_ameliorations"),list) and result["plan_ameliorations"]:
        log(f"Analyse OK: score={result.get('score_actuel','?')} | {len(result['plan_ameliorations'])} tâche(s)","OK")
        return result
    log("JSON invalide → plan défaut","WARN")
    return default_plan()

# ── TASK CONTEXT ──────────────────────────────────────────────────────────────
def task_ctx(task,sources):
    needed=set()
    needed.update(task.get("fichiers_a_modifier",[])); needed.update(task.get("fichiers_a_creer",[]))
    for f in list(needed):
        if f.endswith(".c"): needed.add(f.replace(".c",".h"))
        elif f.endswith(".h"): needed.add(f.replace(".h",".c"))
    needed.update(["kernel/kernel.c","kernel/kernel_entry.asm","kernel/io.h","Makefile","linker.ld"])
    ctx="";used=0
    for f in sorted(needed):
        c=sources.get(f,"")
        content_show=c[:12000] if c and len(c)>12000 else (c or "")
        block=f"--- {f} ---\n{content_show if content_show else '[FICHIER À CRÉER]'}\n\n"
        if used+len(block)>24000: ctx+=f"[{f}: tronqué]\n"; continue
        ctx+=block; used+=len(block)
    return ctx

def impl_prompt(task,ctx):
    nom=task.get("nom","?"); cat=task.get("categorie","?"); cx=task.get("complexite","MOYENNE")
    desc=task.get("description",""); fmod=task.get("fichiers_a_modifier",[])
    fnew=task.get("fichiers_a_creer",[]); fdel=task.get("fichiers_a_supprimer",[])
    return (
        f"{RULES}\n\n{'='*60}\nTÂCHE: {nom}\nCATÉGORIE: {cat} | COMPLEXITÉ: {cx}\n"
        f"FICHIERS À MODIFIER: {fmod}\nFICHIERS À CRÉER: {fnew}\nFICHIERS À SUPPRIMER: {fdel}\n"
        f"{'='*60}\n\nSPÉCIFICATIONS:\n{desc}\n\nCODE EXISTANT:\n{ctx}\n\n"
        f"{'='*60}\nCONTRAINTES ABSOLUES:\n"
        "1. isr.asm: JAMAIS %macro/%rep — isr0:...isr47: EXPLICITEMENT\n"
        "2. outb/inb: UNIQUEMENT dans kernel/io.h static inline\n"
        "3. Makefile DOIT produire os.img via dd (boot.bin seek=0, kernel.bin seek=1)\n"
        "4. Tout nouveau .c → Makefile OBJS\n"
        "5. ZÉRO commentaire, code 100% complet\n"
        "6. #include avec chemins cohérents avec Makefile -I.\n\n"
        "FORMAT:\n=== FILE: chemin/fichier.ext ===\n[code]\n=== END FILE ===\n\nGÉNÈRE:"
    )

# ── AUTO FIX ──────────────────────────────────────────────────────────────────
def auto_fix(build_log, errs, gen_files, bak, model, max_att=4):
    log(f"Auto-fix: {len(errs)} erreur(s)","BUILD")
    _CYCLE_STATS["auto_fixes"]+=1
    cur_log=build_log; cur_errs=errs

    for att in range(1,max_att+1):
        if not cur_errs:
            log(f"Fix {att}: 0 erreurs — build toujours fail (problème non parsable)","WARN")
            # Tenter un fix du Makefile/linker
            _ensure_build_system()
            ok2,cur_log2,cur_errs2=make_build()
            if ok2:
                ensure_osimg()
                _CYCLE_STATS["auto_fix_success"]+=1
                return True,{"attempts":att,"fixed_files":["Makefile"]}
            cur_errs=cur_errs2 if cur_errs2 else ["build fail non résolu par reset Makefile"]
            break

        log(f"Fix {att}/{max_att} — {len(cur_errs)} err","BUILD")
        disc_log(f"🔧 Fix {att}/{max_att}",
                 f"`{len(cur_errs)}` erreur(s)\n"+"\n".join(f"`{e[:60]}`" for e in cur_errs[:3]),0x00AAFF)

        curr_files={}
        for p in gen_files:
            fp=os.path.join(REPO_PATH,p)
            if os.path.exists(fp) and os.path.isfile(fp):
                try:
                    with open(fp,"r",encoding="utf-8",errors="ignore") as f:
                        curr_files[p]=f.read()[:14000]
                except: pass

        file_ctx="".join(f"--- {p} ---\n{c}\n\n" for p,c in curr_files.items())
        err_str="\n".join(cur_errs[:20])
        log_tail=cur_log[-3000:] if len(cur_log)>3000 else cur_log

        diag=[]
        if "multiple definition" in err_str and ("outb" in err_str or "inb" in err_str):
            diag.append("SOLUTION: outb/inb UNIQUEMENT dans kernel/io.h — retirer des autres fichiers")
        if "undefined reference" in err_str and "isr" in err_str.lower():
            diag.append("SOLUTION: Vérifier 'global isr0'...'global isr47' dans isr.asm ET Makefile OBJS")
        if "No such file or directory" in err_str:
            missing=re.findall(r"fatal error: ([^\s:]+):",err_str)
            if missing: diag.append(f"SOLUTION: Créer ou corriger les #include pour: {missing[:5]}")
        if "multiple definition" in err_str and "kernel_main" in err_str:
            diag.append("SOLUTION: kmain dans UN SEUL .c — kernel_entry.asm appelle kmain")
        if "Error 127" in err_str:
            diag.append("SOLUTION: Commande make introuvable — vérifier nasm/gcc/ld dans Makefile")
        if "build fail silencieux" in err_str.lower() or "non parsable" in err_str.lower():
            diag.append("SOLUTION: Probable erreur de linkage silencieuse — vérifier linker.ld ENTRY et SECTIONS")
            diag.append("SOLUTION: Vérifier que tous les .o sont listés dans la règle kernel.bin")
        if "os.img" not in err_str:
            diag.append("RAPPEL: Makefile DOIT avoir règle os.img avec dd if=boot.bin + dd if=kernel.bin seek=1")

        prompt=(
            f"{RULES}\n\n"
            f"ERREURS:\n```\n{err_str}\n```\n\n"
            f"LOG (fin):\n```\n{log_tail}\n```\n\n"
            f"DIAGNOSTICS:\n"+"\n".join(f"⚡ {d}" for d in diag)+"\n\n"
            f"FICHIERS ACTUELS:\n{file_ctx}\n\n"
            "CORRIGER TOUTES LES ERREURS. Code 100% complet, ZÉRO commentaire.\n"
            "Si Makefile: s'assurer que la règle 'all' produit os.img via dd.\n"
            "FORMAT:\n=== FILE: fichier ===\n[code]\n=== END FILE ==="
        )

        resp=ai_call(prompt,max_tokens=32768,timeout=130,tag=f"fix/{att}")
        if not resp: time.sleep(min(8*(2**(att-1)),45)); continue

        new_files,_=parse_ai_files(resp)
        if not new_files: log(f"Fix {att}: parse vide","WARN"); time.sleep(min(5*(2**(att-1)),30)); continue

        write_files(new_files)
        ok,cur_log,cur_errs=make_build()

        if ok:
            ensure_osimg()
            m_u=alive()[0]["model"] if alive() else model
            git_push("fix: build",list(new_files.keys()),f"auto-fix {len(errs)}→0",m_u)
            disc_now("🔧 Fix ✅",f"**{len(errs)} err** → **0** en {att} tentative(s)",0x00AAFF)
            _CYCLE_STATS["auto_fix_success"]+=1
            return True,{"attempts":att,"fixed_files":list(new_files.keys())}

        log(f"Fix {att}: {len(cur_errs)} erreur(s) restantes","WARN")
        time.sleep(min(6*(2**(att-1)),35))

    _CYCLE_STATS["auto_fix_fail"]+=1
    return False,{"attempts":max_att,"remaining_errors":cur_errs[:5]}

# ── PRE-FLIGHT ────────────────────────────────────────────────────────────────
def pre_flight_check():
    log("Pre-flight: vérification build initial...","BUILD")
    _ensure_build_system()
    ok,log_text,errs=make_build()
    if ok:
        ensure_osimg()
        img_path=os.path.join(REPO_PATH,"os.img")
        if os.path.exists(img_path):
            log(f"os.img: {os.path.getsize(img_path)} bytes ✅","OK")
        log("Pre-flight: build OK ✅","OK")
        return True,[]
    log(f"Pre-flight: build cassé ({len(errs)} err)","WARN")
    disc_now("⚠️ Build pré-existant cassé",
             f"`{len(errs)}` erreur(s)\n"+"\n".join(f"`{e[:75]}`" for e in errs[:4]),0xFF6600)
    return False,errs

# ── IMPLEMENT TASK ────────────────────────────────────────────────────────────
def implement(task,sources,i,total):
    nom=task.get("nom",f"Tâche {i}"); cat=task.get("categorie","?")
    prio=task.get("priorite","?"); cx=task.get("complexite","MOYENNE")
    desc=task.get("description",""); f_mod=task.get("fichiers_a_modifier",[])
    f_new=task.get("fichiers_a_creer",[]); model=alive()[0]["model"] if alive() else "?"

    log(f"\n{'='*56}\n[{i}/{total}] [{prio}] {nom}\n{'='*56}")
    disc_now(f"🚀 [{i}/{total}] {nom[:55]}",
             f"```\n{pbar(int((i-1)/total*100))}\n```\n{desc[:280]}",0xFFA500,
             [{"name":"🎯","value":prio,"inline":True},{"name":"📁","value":cat,"inline":True},
              {"name":"⚙️","value":cx,"inline":True},
              {"name":"📝 Modifier","value":"\n".join(f"`{f}`" for f in f_mod[:5]) or "—","inline":True},
              {"name":"✨ Créer","value":"\n".join(f"`{f}`" for f in f_new[:5]) or "—","inline":True},
              {"name":"🔑 Providers","value":prov_summary()[:400],"inline":False}])

    t0=time.time(); ctx=task_ctx(task,sources)
    max_tok={"HAUTE":32768,"MOYENNE":24576,"BASSE":12288,"TRES HAUTE":32768}.get(cx,24576)
    prompt=impl_prompt(task,ctx)
    resp=ai_call(prompt,max_tokens=max_tok,timeout=200,tag=f"impl/{nom[:16]}")
    elapsed=round(time.time()-t0,1)

    if not resp:
        disc_now(f"❌ [{i}/{total}] {nom[:50]}",f"Providers indisponibles après {elapsed}s",0xFF4444)
        return False,[],[],{"nom":nom,"elapsed":elapsed,"result":"ai_fail","errors":[],"model":model}

    files,to_del=parse_ai_files(resp)
    if not files and not to_del:
        disc_now(f"❌ [{i}/{total}] {nom[:50]}",f"Réponse {len(resp):,}c mais aucun fichier",0xFF6600,
                 [{"name":"Début","value":f"```\n{resp[:300]}\n```","inline":False}])
        return False,[],[],{"nom":nom,"elapsed":elapsed,"result":"parse_empty","errors":[],"model":model}

    disc_log(f"📁 {len(files)} fichier(s)",
             "\n".join(f"`{f}` → {len(c):,}c" for f,c in list(files.items())[:10]),0x00AAFF)

    bak_f=backup(list(files.keys()))
    written=write_files(files); deleted=del_files(to_del)
    if not written and not deleted:
        return False,[],[],{"nom":nom,"elapsed":elapsed,"result":"no_files_written","errors":[],"model":model}

    ok,build_log,errs=make_build()

    if ok:
        ensure_osimg()
        img_ok=os.path.exists(os.path.join(REPO_PATH,"os.img"))
        pushed,sha,commit_short=git_push(nom,written+deleted,desc,model)
        total_elapsed=round(time.time()-t0,1)

        if pushed and sha:
            m={"nom":nom,"elapsed":total_elapsed,"result":"success","sha":sha,
               "files":written+deleted,"model":model,"fix_count":0,"img_ok":img_ok}
            disc_now(f"✅ [{i}/{total}] {nom[:50]}",
                     f"```\n{pbar(int(i/total*100))}\n```\nCommit: `{sha}`\nos.img: {'✅' if img_ok else '❌'}",
                     0x00FF88,
                     [{"name":"⏱️","value":f"{total_elapsed:.0f}s","inline":True},
                      {"name":"📁","value":str(len(written+deleted)),"inline":True},
                      {"name":"🤖","value":model[:30],"inline":True},
                      {"name":"💾 os.img","value":"✅ Bootable" if img_ok else "❌ Manquant","inline":True}])
            return True,written,deleted,m

        elif pushed and sha is None:
            disc_log(f"✅ [{i}/{total}] {nom[:50]} (déjà à jour)","",0x00AA44)
            return True,[],[],{"nom":nom,"elapsed":total_elapsed,"result":"success_no_change",
                                "sha":git_sha(),"files":[],"model":model,"fix_count":0}
        else:
            restore(bak_f)
            return False,[],[],{"nom":nom,"elapsed":elapsed,"result":"push_fail","errors":[],"model":model}

    fixed,fix_meta=auto_fix(build_log,errs,list(files.keys()),bak_f,model)

    if fixed:
        total_elapsed=round(time.time()-t0,1); fc=fix_meta.get("attempts",0)
        img_ok=os.path.exists(os.path.join(REPO_PATH,"os.img"))
        m={"nom":nom,"elapsed":total_elapsed,"result":"success_after_fix",
           "sha":git_sha(),"files":written+deleted,"model":model,"fix_count":fc,"img_ok":img_ok}
        disc_now(f"✅ [{i}/{total}] {nom[:50]} (fix×{fc})",
                 f"```\n{pbar(int(i/total*100))}\n```\nos.img: {'✅' if img_ok else '❌'}",0x00BB66,
                 [{"name":"⏱️","value":f"{total_elapsed:.0f}s","inline":True},
                  {"name":"🔧","value":f"{fc} fix","inline":True},
                  {"name":"🤖","value":model[:30],"inline":True}])
        return True,written,deleted,m

    restore(bak_f)
    for p in written:
        if p not in bak_f:
            fp=os.path.join(REPO_PATH,p)
            if os.path.exists(fp) and os.path.isfile(fp):
                try: os.remove(fp)
                except: pass
    SOURCE_CACHE["hash"]=None
    total_elapsed=round(time.time()-t0,1)
    remaining_errs=fix_meta.get("remaining_errors",errs[:5])
    es="\n".join(f"`{e[:80]}`" for e in remaining_errs[:5])
    disc_now(f"❌ [{i}/{total}] {nom[:50]}",
             f"Build fail après {fix_meta.get('attempts',0)} fix(es) — restauré",0xFF4444,
             [{"name":"Erreurs","value":es[:900] or "?","inline":False},
              {"name":"⏱️","value":f"{total_elapsed:.0f}s","inline":True}])
    return False,[],[],{"nom":nom,"elapsed":total_elapsed,"result":"build_fail",
                        "errors":remaining_errs[:5],"model":model}

# ── ISSUES / PRs ──────────────────────────────────────────────────────────────
BOT_LOGINS=frozenset({"MaxOS-AI-Bot","github-actions[bot]","dependabot[bot]","maxos-ai[bot]"})

def _bot_already_commented(n):
    comments=gh_issue_comments(n)
    return any(c.get("user",{}).get("login","") in BOT_LOGINS for c in (comments or []))

def handle_issues(ms_cache=None):
    if ms_cache is None: ms_cache={}
    issues=gh_open_issues()
    if not issues: log("Issues: aucune"); return ms_cache
    log(f"Issues: {len(issues)} ouverte(s)")
    treated=0
    for issue in issues[:8]:
        n=issue.get("number"); title=issue.get("title","")
        author=issue.get("user",{}).get("login","")
        body_t=(issue.get("body","") or "")[:800]
        labels=[l.get("name","") for l in issue.get("labels",[])]
        if issue.get("state")!="open": continue
        if author in BOT_LOGINS: continue
        if _bot_already_commented(n): continue
        if not watchdog(): break
        log(f"Issue #{n}: {title[:65]}")
        prompt=(f"Bot GitHub MaxOS. ISSUE #{n}\nTitre: {title}\nAuteur: {author}\n"
                f"Labels: {', '.join(labels) or 'aucun'}\nCorps:\n{body_t}\n\n"
                'JSON valide uniquement:\n{"type":"bug|enhancement|question|invalid","priority":"critical|high|medium|low",'
                '"component":"kernel|driver|app|build|doc|other","labels_add":["bug"],'
                '"action":"respond|close|label_only","response":"réponse utile en français"}')
        a=_parse_json_robust(ai_call(prompt,max_tokens=800,timeout=40,tag=f"issue/{n}"))
        if not a: continue
        action=a.get("action","label_only")
        lbl_add=[l for l in a.get("labels_add",[]) if l in STANDARD_LABELS]
        if "ai-reviewed" not in lbl_add: lbl_add.append("ai-reviewed")
        if lbl_add: gh_add_labels(n,lbl_add)
        resp_t=a.get("response","")
        if resp_t and action in ("respond","close"):
            gh_post_comment(n,f"## 🤖 MaxOS AI\n\n{resp_t}\n\n---\n*MaxOS AI v{VERSION}*")
        if action=="close": gh_close_issue(n,"completed")
        disc_log(f"🎫 Issue #{n}",f"**{title[:45]}** | `{action}`",0x5865F2)
        treated+=1; time.sleep(1)
    log(f"Issues: {treated} traitée(s)")
    return ms_cache

def handle_stale(days_stale=21,days_close=7):
    issues=gh_open_issues(); now=time.time(); marked=closed=0
    for issue in issues:
        n=issue.get("number"); upd=issue.get("updated_at","")
        labels=[l.get("name","") for l in issue.get("labels",[])]
        author=issue.get("user",{}).get("login","")
        if author in BOT_LOGINS: continue
        if any(l in labels for l in ("wontfix","security","bug")): continue
        is_stale="stale" in labels
        try: upd_ts=datetime.strptime(upd,"%Y-%m-%dT%H:%M:%SZ").timestamp()
        except: continue
        age=now-upd_ts
        if age>=(days_stale+days_close)*86400 and is_stale:
            gh_post_comment(n,f"🤖 Fermeture après **{int(age/86400)}j** d'inactivité.")
            gh_close_issue(n,"not_planned"); closed+=1
        elif age>=days_stale*86400 and not is_stale:
            gh_add_labels(n,["stale"])
            gh_post_comment(n,f"⏰ Inactive depuis **{int(age/86400)}j**. Fermeture dans {days_close}j.")
            marked+=1
    if marked+closed: log(f"Stale: {marked} marquées, {closed} fermées")

def handle_prs():
    prs=gh_open_prs()
    if not prs: log("PRs: aucune"); return
    log(f"PRs: {len(prs)} ouverte(s)"); reviewed=0
    for pr in prs[:5]:
        n=pr.get("number"); title=pr.get("title",""); author=pr.get("user",{}).get("login","")
        if pr.get("state")!="open": continue
        if author in BOT_LOGINS: continue
        revs=gh_pr_reviews(n)
        if any(r.get("user",{}).get("login","") in BOT_LOGINS for r in (revs or [])): continue
        if not watchdog(): break
        files_d=gh_pr_files(n); patches=""
        for f in files_d[:5]:
            if f.get("filename","").endswith((".c",".h",".asm")):
                p=f.get("patch","")[:1500]
                if p: patches+=f"\n--- {f.get('filename','')} ---\n{p}\n"
        prompt=(f"Expert code review MaxOS bare metal x86.\n{RULES}\nPR #{n}: {title}\nAuteur: {author}\n"
                f"Diff:\n{patches}\n\n"
                'JSON:\n{"decision":"APPROVE|REQUEST_CHANGES|COMMENT","summary":"2 phrases",'
                '"problems":[],"positives":[],"bare_metal_violations":[],"merge_safe":false}')
        a=_parse_json_robust(ai_call(prompt,max_tokens=2000,timeout=60,tag=f"pr/{n}"))
        if not a: a={}
        decision=a.get("decision","COMMENT"); merge_safe=a.get("merge_safe",False)
        icon={"APPROVE":"✅","REQUEST_CHANGES":"🔴","COMMENT":"💬"}.get(decision,"💬")
        body=(f"## {icon} Code Review MaxOS AI — PR #{n}\n\n{a.get('summary','Analyse N/A.')}\n\n")
        if a.get("problems"): body+="### ❌ Problèmes\n"+"\n".join(f"- {p}" for p in a["problems"][:6])+"\n\n"
        if a.get("bare_metal_violations"): body+="### ⚠️ Violations\n"+"\n".join(f"- {v}" for v in a["bare_metal_violations"][:5])+"\n\n"
        if a.get("positives"): body+="### ✅ Positifs\n"+"\n".join(f"- {p}" for p in a["positives"][:5])+"\n\n"
        body+=f"\n---\n*MaxOS AI v{VERSION}*"
        if decision=="APPROVE" and merge_safe: gh_approve_pr(n,body); gh_add_labels(n,["ai-approved","ai-reviewed"])
        elif decision=="REQUEST_CHANGES": gh_req_changes(n,body); gh_add_labels(n,["ai-rejected","ai-reviewed"])
        else: gh_post_review(n,body,"COMMENT"); gh_add_labels(n,["ai-reviewed"])
        disc_log(f"📋 PR #{n} — {decision}",f"**{title[:45]}**",0x00AAFF)
        reviewed+=1; time.sleep(1)
    log(f"PRs: {reviewed} reviewée(s)")

# ── RELEASE ───────────────────────────────────────────────────────────────────
def create_release(tasks_done,tasks_failed,analyse,stats):
    releases=gh_list_releases(10); last_tag="v0.0.0"
    for r in releases:
        tag=r.get("tag_name","")
        if re.match(r"v\d+\.\d+\.\d+",tag): last_tag=tag; break
    try:
        pts=last_tag.lstrip("v").split(".")
        major,minor,patch=int(pts[0]),int(pts[1]),int(pts[2])
    except: major=minor=patch=0

    score=analyse.get("score_actuel",35)
    if score>=80: major+=1; minor=0; patch=0
    elif score>=60: minor+=1; patch=0
    else: patch+=1
    new_tag=f"v{major}.{minor}.{patch}"

    img_path=os.path.join(REPO_PATH,"os.img")
    img_ok=os.path.exists(img_path) and os.path.getsize(img_path)>512
    img_size=os.path.getsize(img_path) if img_ok else 0

    compare=gh_compare(last_tag,"HEAD"); commits=compare.get("commits",[])
    ahead_by=compare.get("ahead_by",len(commits))
    chg_lines=[]
    for c in commits[:20]:
        sha=c.get("sha","")[:7]; msg=c.get("commit",{}).get("message","").split("\n")[0][:80]
        if msg and not msg.startswith("[skip"): chg_lines.append(f"- `{sha}` {msg}")
    changelog="\n".join(chg_lines) or "- Maintenance"

    changes_ok="".join(
        f"- ✅ **{t.get('nom','?')[:50]}** [`{t.get('sha','?')[:7]}`]"
        f"{' (fix×'+str(t['fix_count'])+')' if t.get('fix_count',0)>0 else ''} — {t.get('elapsed',0):.0f}s\n"
        for t in tasks_done)
    changes_fail=("\n## ⏭️ Reporté\n\n"+"\n".join(f"- ❌ {n}" for n in tasks_failed)+"\n") if tasks_failed else ""

    tk=sum(p["tokens"] for p in PROVIDERS); calls=sum(p["calls"] for p in PROVIDERS)
    now=datetime.utcnow()
    prov_table=""
    for p in sorted(PROVIDERS,key=lambda x:-x["calls"]):
        if p["calls"]==0: continue
        st="💀" if p["dead"] else "🟢"
        prov_table+=f"| {st} `{p['id']}` | {p['calls']} | ~{p['tokens']:,} | {avg_rt(p):.1f}s |\n"

    body=(
        f"# 🖥️ MaxOS {new_tag}\n\n> 🤖 Généré par **MaxOS AI v{VERSION}**\n\n---\n\n"
        f"## 📊 État\n\n| Métrique | Valeur |\n|---|---|\n"
        f"| 🎯 Score | **{score}/100** |\n"
        f"| 📈 Niveau | {analyse.get('niveau_os','?')} |\n"
        f"| 📁 Fichiers | {stats.get('files',0)} |\n"
        f"| 📝 Lignes | {stats.get('lines',0):,} |\n"
        f"| 💾 os.img | {'✅ '+str(img_size)+' bytes' if img_ok else '❌ non généré'} |\n\n"
        f"## ✅ Améliorations ({len(tasks_done)})\n\n{changes_ok or '*(aucune)*'}"
        f"{changes_fail}\n"
        f"## 🚀 Tester\n\n```bash\n"
        f"qemu-system-i386 -drive format=raw,file=os.img,if=floppy -boot a -vga std -k fr -m 32\n"
        f"```\n\n"
        f"## 📝 Changelog {last_tag} → {new_tag} ({ahead_by} commits)\n\n{changelog}\n\n"
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

    pre=score<50
    release_data=gh_create_release(new_tag,
                                    f"MaxOS {new_tag} — {analyse.get('niveau_os','?')} — {now.strftime('%Y-%m-%d')}",
                                    body,pre=pre)

    if release_data:
        release_id=release_data.get("id")
        release_url=release_data.get("html_url","?")
        log(f"Release {new_tag} créée: {release_url}","OK")

        # Upload os.img comme asset de la release
        if img_ok and release_id:
            asset_url=gh_upload_asset(release_id,img_path,"os.img")
            if asset_url:
                log(f"os.img uploadé dans la release: {asset_url}","OK")

        disc_now(f"🚀 Release {new_tag} !",
                 f"Score: **{score}/100** | os.img: {'✅ '+str(img_size)+' bytes' if img_ok else '❌'}",
                 0x00FF88 if not pre else 0xFFA500,
                 [{"name":"🏷️ Version","value":new_tag,"inline":True},
                  {"name":"📊 Score","value":f"{score}/100","inline":True},
                  {"name":"💾 os.img","value":"✅ Bootable" if img_ok else "❌ Manquant","inline":True},
                  {"name":"🔗 Lien","value":f"[Release]({release_url})","inline":False}])
    else:
        log("Release: échec","ERROR")
    return release_data

def final_report(success,total,tasks_done,tasks_failed,analyse,stats):
    score=analyse.get("score_actuel",35); pct=int(success/total*100) if total>0 else 0
    color=0x00FF88 if pct>=80 else 0xFFA500 if pct>=50 else 0xFF4444
    elapsed=int(time.time()-START_TIME); tk=sum(p["tokens"] for p in PROVIDERS)
    img_ok=os.path.exists(os.path.join(REPO_PATH,"os.img"))
    sources=read_all(); qual=analyze_quality(sources)
    done_s="\n".join(f"✅ {t.get('nom','?')[:42]} ({t.get('elapsed',0):.0f}s)"+(f" fix×{t['fix_count']}" if t.get("fix_count",0)>0 else "") for t in tasks_done) or "Aucune"
    fail_s="\n".join(f"❌ {n[:42]}" for n in tasks_failed) or "Aucune"
    disc_now(f"🏁 Cycle — {success}/{total}",
             f"```\n{pbar(pct)}\n```\n**{pct}%** | os.img: {'✅' if img_ok else '❌'}",color,
             [{"name":"✅","value":str(success),"inline":True},
              {"name":"❌","value":str(total-success),"inline":True},
              {"name":"⏱️","value":f"{elapsed}s","inline":True},
              {"name":"💬 Tokens","value":f"{tk:,}","inline":True},
              {"name":"📊 Qualité","value":f"{qual['score']}/100","inline":True},
              {"name":"💾 os.img","value":"✅ OK" if img_ok else "❌ Manquant","inline":True},
              {"name":"✅ Réussies","value":done_s[:900],"inline":False},
              {"name":"❌ Échouées","value":fail_s[:500],"inline":False},
              {"name":"🔑 Providers","value":prov_summary()[:600],"inline":False}])

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print("="*64)
    print(f"  MaxOS AI Developer v{VERSION}")
    print(f"  Ultra-robuste | Multi-provider | Bare metal x86")
    print("="*64)
    if not PROVIDERS: print("FATAL: Aucun provider IA."); sys.exit(1)

    by_type=defaultdict(list)
    for p in PROVIDERS: by_type[p["type"]].append(p)
    for t in sorted(by_type.keys()):
        ps=by_type[t]; ku=len(set(p["key"][:8] for p in ps)); mu=len(set(p["model"] for p in ps))
        print(f"  {t:12s}: {ku} clé(s) × {mu} modèle(s) = {len(ps)} providers")
    print(f"  {'TOTAL':12s}: {len(PROVIDERS)} providers")
    print(f"  {'RUNTIME':12s}: {MAX_RUNTIME}s max | DEBUG: {'ON' if DEBUG else 'OFF'}")
    print("="*64+"\n")

    disc_now(f"🤖 MaxOS AI v{VERSION} — Démarrage",f"`{len(PROVIDERS)}` providers",0x5865F2,
             [{"name":"🔑 Providers","value":prov_summary()[:800],"inline":False},
              {"name":"📁 Repo","value":f"`{REPO_OWNER}/{REPO_NAME}`","inline":True},
              {"name":"⏱️ Runtime","value":f"{MAX_RUNTIME}s max","inline":True}])

    subprocess.run(["make","clean"],cwd=REPO_PATH,capture_output=True,timeout=30)
    log("Setup: labels GitHub..."); gh_ensure_labels(STANDARD_LABELS)
    ms_cache={}

    log("[Issues] Traitement..."); ms_cache=handle_issues(ms_cache) or ms_cache
    if not watchdog(): sys.exit(0)
    log("[Stale] Vérification..."); handle_stale()
    if not watchdog(): sys.exit(0)
    log("[PRs] Traitement..."); handle_prs()
    if not watchdog(): sys.exit(0)

    log("[Pre-flight] Build initial..."); pf_ok,pf_errs=pre_flight_check()

    sources=read_all(force=True); stats=proj_stats(sources); qual=analyze_quality(sources)
    log(f"Sources: {stats['files']} fichiers | {stats['lines']:,} lignes")
    log(f"Qualité: {qual['score']}/100 | {len(qual['violations'])} violation(s)")

    disc_now("📊 Sources",f"`{stats['files']}` fichiers | `{stats['lines']:,}` lignes",0x5865F2,
             [{"name":"Qualité","value":f"{qual['score']}/100","inline":True},
              {"name":"C","value":f"{qual['c_files']} .c/.h","inline":True},
              {"name":"ASM","value":f"{qual['asm_files']} .asm","inline":True}])

    analyse=phase_analyse(build_ctx(sources),stats)
    score=analyse.get("score_actuel",35); niveau=analyse.get("niveau_os","?")
    plan=analyse.get("plan_ameliorations",[]); milestone=analyse.get("prochaine_milestone","?")
    features=analyse.get("fonctionnalites_presentes",[]); manques=analyse.get("fonctionnalites_manquantes_critiques",[])

    order={"CRITIQUE":0,"HAUTE":1,"NORMALE":2,"BASSE":3,"ELEVEE":1,"FAIBLE":3}
    plan=sorted(plan,key=lambda t:(order.get(t.get("priorite","NORMALE"),2),t.get("nom","")))
    log(f"Score={score}/100 | {niveau} | {len(plan)} tâche(s)","STAT")

    if milestone and milestone not in ms_cache:
        ms_num=gh_ensure_milestone(milestone,f"Objectif: {milestone}")
        if ms_num: ms_cache[milestone]=ms_num

    disc_now(f"📊 Analyse: {score}/100",f"```\n{pbar(score)}\n```",
             0x00AAFF if score>=60 else 0xFFA500 if score>=30 else 0xFF4444,
             [{"name":"✅ Présentes","value":"\n".join(f"+ {f}" for f in features[:6]) or "—","inline":True},
              {"name":"❌ Manquantes","value":"\n".join(f"- {f}" for f in manques[:6]) or "—","inline":True},
              {"name":"📋 Plan","value":"\n".join(f"[{i+1}] `{t.get('priorite','?')[:3]}` {t.get('nom','?')[:38]}" for i,t in enumerate(plan[:8])) or "—","inline":False},
              {"name":"🎯 Milestone","value":milestone[:80],"inline":True}])

    total=len(plan); success=0; tasks_done=[]; tasks_failed=[]

    for i,task in enumerate(plan,1):
        if not watchdog(): log(f"Watchdog: arrêt avant tâche {i}/{total}","WARN"); break
        if remaining_time()<200: log(f"Moins de 200s restantes — arrêt","WARN"); break
        disc_log(f"💓 [{i}/{total}] {task.get('nom','?')[:45]}",
                 f"Uptime: {uptime()} | Reste: {int(remaining_time())}s\n{prov_summary()[:250]}",0x7289DA)
        sources_now=read_all()
        ok,written,deleted,metrics=implement(task,sources_now,i,total)
        TASK_METRICS.append(metrics)
        if ok: success+=1; tasks_done.append(metrics)
        else: tasks_failed.append(task.get("nom","?"))
        if i<total and watchdog():
            n_al=len(alive()); pause=3 if n_al>=5 else 6 if n_al>=3 else 12 if n_al>=1 else 20
            log(f"Pause {pause}s ({n_al} dispo, {int(remaining_time())}s restants)")
            _flush_disc(True); time.sleep(pause)

    log(f"\n{'='*56}\nCYCLE TERMINÉ: {success}/{total}\n{'='*56}")

    # S'assurer que os.img existe avant la release
    ensure_osimg()

    sf=read_all(force=True)
    if success>0:
        log("[Release] Création...")
        create_release(tasks_done,tasks_failed,analyse,proj_stats(sf))
    else:
        log("[Release] 0 succès — pas de release")

    final_report(success,total,tasks_done,tasks_failed,analyse,proj_stats(sf))
    _flush_disc(True)

    print(f"\n{'='*64}")
    img_ok=os.path.exists(os.path.join(REPO_PATH,"os.img"))
    img_size=os.path.getsize(os.path.join(REPO_PATH,"os.img")) if img_ok else 0
    print(f"[FIN] {success}/{total} | uptime: {uptime()} | GH RL: {GH_RATE['remaining']}")
    print(f"      os.img: {'✅ '+str(img_size)+' bytes' if img_ok else '❌ MANQUANT'}")
    print(f"      IA calls: {_CYCLE_STATS.get('ai_calls',0)} | 429: {_CYCLE_STATS.get('total_429',0)}")
    for t in tasks_done:
        fc=t.get("fix_count",0)
        print(f"  ✅ {t.get('nom','?')[:58]} ({t.get('elapsed',0):.0f}s){' fix×'+str(fc) if fc else ''}")
    for n in tasks_failed: print(f"  ❌ {n[:58]}")
    print("="*64)

if __name__=="__main__":
    main()
