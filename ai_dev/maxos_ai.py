#!/usr/bin/env python3
import os, sys, json, time, subprocess, re, hashlib, traceback
import urllib.request, urllib.error
from datetime import datetime, timezone

VERSION     = "13.0"
DEBUG       = os.environ.get("MAXOS_DEBUG","0") == "1"
START_TIME  = time.time()
MAX_RUNTIME = 3200

REPO_OWNER = os.environ.get("REPO_OWNER","MaxLananas")
REPO_NAME  = os.environ.get("REPO_NAME","MaxOS")
REPO_PATH  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GH_TOKEN   = os.environ.get("GH_PAT","") or os.environ.get("GITHUB_TOKEN","")
DISCORD_WH = os.environ.get("DISCORD_WEBHOOK","")

GEMINI_MODELS = [
    ("gemini-2.5-flash",        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"),
    ("gemini-2.0-flash",        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"),
    ("gemini-2.0-flash-lite",   "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent"),
    ("gemini-1.5-flash",        "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"),
]

OPENROUTER_MODELS = [
    "google/gemini-2.0-flash-exp:free",
    "qwen/qwen-2.5-coder-32b-instruct:free",
    "deepseek/deepseek-r1-distill-llama-70b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "microsoft/phi-4-reasoning:free",
    "google/gemini-flash-1.5:free",
    "nousresearch/deephermes-3-llama-3-8b:free",
]

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
    "mixtral-8x7b-32768",
]

def load_providers():
    providers = []

    for i in range(1, 10):
        suffix = "" if i == 1 else f"_{i}"
        key    = os.environ.get(f"GEMINI_API_KEY{suffix}", "").strip()
        if not key:
            continue
        for model_name, base_url in GEMINI_MODELS:
            providers.append({
                "type":      "gemini",
                "id":        f"gem{i}_{model_name[:12]}",
                "key":       key,
                "model":     model_name,
                "url":       f"{base_url}?key={key}",
                "cooldown":  0,
                "errors":    0,
                "calls":     0,
                "tokens":    0,
                "dead":      False,
            })

    for i in range(1, 10):
        suffix = "" if i == 1 else f"_{i}"
        key    = os.environ.get(f"OPENROUTER_KEY{suffix}", "").strip()
        if not key:
            continue
        for model_name in OPENROUTER_MODELS:
            short = model_name.split("/")[-1].replace(":free","")[:14]
            providers.append({
                "type":      "openrouter",
                "id":        f"or{i}_{short}",
                "key":       key,
                "model":     model_name,
                "url":       "https://openrouter.ai/api/v1/chat/completions",
                "cooldown":  0,
                "errors":    0,
                "calls":     0,
                "tokens":    0,
                "dead":      False,
            })

    for i in range(1, 10):
        suffix = "" if i == 1 else f"_{i}"
        key    = os.environ.get(f"GROQ_KEY{suffix}", "").strip()
        if not key:
            continue
        for model_name in GROQ_MODELS:
            providers.append({
                "type":      "groq",
                "id":        f"groq{i}_{model_name[:14]}",
                "key":       key,
                "model":     model_name,
                "url":       "https://api.groq.com/openai/v1/chat/completions",
                "cooldown":  0,
                "errors":    0,
                "calls":     0,
                "tokens":    0,
                "dead":      False,
            })

    for i in range(1, 5):
        suffix = "" if i == 1 else f"_{i}"
        key    = os.environ.get(f"MISTRAL_KEY{suffix}", "").strip()
        if not key:
            continue
        for model_name in ["mistral-small-latest", "open-mistral-7b"]:
            providers.append({
                "type":      "mistral",
                "id":        f"mis{i}_{model_name[:14]}",
                "key":       key,
                "model":     model_name,
                "url":       "https://api.mistral.ai/v1/chat/completions",
                "cooldown":  0,
                "errors":    0,
                "calls":     0,
                "tokens":    0,
                "dead":      False,
            })

    return providers

PROVIDERS = load_providers()
PROV_IDX  = 0

GH_RATE      = {"remaining": 5000, "reset": 0}
SOURCE_CACHE = {"hash": None, "data": None}
TASK_METRICS = []
DISC_BUFFER  = []
DISC_LAST    = 0.0
DISC_INTERVAL = 20

def ts():
    return datetime.now(timezone.utc).strftime("%H:%M:%S")

def uptime():
    s = int(time.time() - START_TIME)
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def log(msg, level="INFO"):
    icons = {"INFO":"📋","WARN":"⚠️","ERROR":"❌","OK":"✅",
             "BUILD":"🔨","GIT":"📦","TIME":"⏱️"}
    print(f"[{ts()}] {icons.get(level,'📋')} {msg}", flush=True)

def pbar(pct, w=20):
    f = int(w * pct / 100)
    return "█"*f + "░"*(w-f) + f" {pct}%"

def mask(k):
    return k[:8]+"***"+k[-4:] if len(k) > 12 else "***"

def watchdog():
    if time.time() - START_TIME >= MAX_RUNTIME:
        log(f"Watchdog: {MAX_RUNTIME}s atteint","WARN")
        disc_force("⏰ Watchdog", f"Arrêt après {uptime()}", 0xFFA500)
        return False
    return True

def providers_alive():
    now = time.time()
    return [p for p in PROVIDERS if not p["dead"] and now >= p["cooldown"]]

def providers_summary():
    now     = time.time()
    alive   = providers_alive()
    total   = sum(1 for p in PROVIDERS if not p["dead"])
    by_type = {}
    for p in PROVIDERS:
        if p["dead"]: continue
        t  = p["type"]
        st = "🟢" if now >= p["cooldown"] else f"🔴{int(p['cooldown']-now)}s"
        by_type.setdefault(t, []).append(f"{st}")
    lines = [f"**{t}**: " + " ".join(v[:4]) for t,v in by_type.items()]
    return f"{len(alive)}/{total} actifs\n" + "\n".join(lines)

def get_provider():
    global PROV_IDX
    now   = time.time()
    alive = [p for p in PROVIDERS if not p["dead"] and now >= p["cooldown"]]
    if alive:
        p   = min(alive, key=lambda x: x["cooldown"])
        idx = PROVIDERS.index(p)
        PROV_IDX = idx
        return idx, p
    live = [p for p in PROVIDERS if not p["dead"]]
    if not live:
        log("FATAL: tous providers dead","ERROR")
        disc_force("💀 Tous providers dead", "Arrêt forcé.", 0xFF0000)
        sys.exit(1)
    best  = min(live, key=lambda x: x["cooldown"])
    idx   = PROVIDERS.index(best)
    wait  = best["cooldown"] - now + 0.5
    log(f"Tous en cooldown → attente {int(wait)}s","TIME")
    disc_force("⏳ Cooldown global",
               f"Attente **{int(wait)}s**\n{providers_summary()}",
               0xFF8800)
    time.sleep(max(wait, 0.5))
    PROV_IDX = idx
    return idx, best

def penalize(idx, secs, dead=False):
    p = PROVIDERS[idx]
    if dead:
        p["dead"] = True
        log(f"Provider {p['id']} ({p['type']}) → DEAD","ERROR")
        return
    p["cooldown"] = time.time() + secs
    p["errors"]  += 1
    log(f"Provider {p['id']} → cooldown {secs}s (errs={p['errors']})","WARN")

def call_gemini(p, prompt, max_tokens, timeout):
    payload = json.dumps({
        "contents": [{"parts":[{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.05}
    }).encode("utf-8")
    req = urllib.request.Request(
        p["url"], data=payload,
        headers={"Content-Type":"application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode("utf-8"))
    cands = data.get("candidates",[])
    if not cands: return None
    c      = cands[0]
    finish = c.get("finishReason","STOP")
    if finish in ("SAFETY","RECITATION"): return None
    parts  = c.get("content",{}).get("parts",[])
    texts  = [p2.get("text","") for p2 in parts
              if isinstance(p2,dict) and not p2.get("thought") and p2.get("text")]
    result = "".join(texts)
    return result if result else None

def call_openai_compat(p, prompt, max_tokens, timeout):
    payload = json.dumps({
        "model":       p["model"],
        "messages":    [{"role":"user","content": prompt}],
        "max_tokens":  min(max_tokens, 32768),
        "temperature": 0.05,
    }).encode("utf-8")
    headers = {
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {p['key']}",
    }
    if p["type"] == "openrouter":
        headers["HTTP-Referer"] = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
        headers["X-Title"]      = "MaxOS AI Developer"
    req = urllib.request.Request(p["url"], data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode("utf-8"))
    choices = data.get("choices",[])
    if not choices: return None
    content = choices[0].get("message",{}).get("content","")
    return content if content else None

def ai_call(prompt, max_tokens=32768, timeout=150, tag="?"):
    if len(prompt) > 55000:
        prompt = prompt[:55000] + "\n[TRONQUÉ]"

    max_attempts = min(len(PROVIDERS) * 2, 30)

    for attempt in range(1, max_attempts+1):
        if not watchdog():
            return None

        idx, p = get_provider()
        log(f"[{tag}] {p['type']}/{p['id']} attempt={attempt}")

        disc_log(f"🤖 [{tag}] attempt {attempt}",
                 f"`{p['type']}` | `{p['model'][:35]}` | `{mask(p['key'])}`\n"
                 f"uptime `{uptime()}`",
                 0x5865F2)

        try:
            t0 = time.time()
            if p["type"] == "gemini":
                text = call_gemini(p, prompt, max_tokens, timeout)
            else:
                text = call_openai_compat(p, prompt, max_tokens, timeout)
            elapsed = round(time.time()-t0, 1)

            if text is None:
                log(f"[{tag}] Réponse vide ({p['id']})","WARN")
                penalize(idx, 30)
                continue

            est_tk      = len(text)//4
            p["calls"] += 1
            p["tokens"]+= est_tk
            log(f"[{tag}] ✅ {len(text)} chars en {elapsed}s (~{est_tk}tk)","OK")
            disc_log(f"✅ [{tag}] OK",
                     f"`{len(text):,}` chars | `{elapsed}s` | ~`{est_tk}` tokens\n"
                     f"`{p['type']}` | `{p['model'][:30]}`",
                     0x00FF88)
            return text

        except urllib.error.HTTPError as e:
            elapsed = round(time.time()-t0, 1)
            body    = ""
            try: body = e.read().decode()[:400]
            except: pass

            log(f"[{tag}] HTTP {e.code} ({p['id']}) {elapsed}s","WARN")
            disc_log(f"⚠️ [{tag}] HTTP {e.code} — {p['type']}/{p['model'][:20]}",
                     f"`{body[:200]}`", 0xFF4400)

            if e.code == 429:
                wait = min(60 * (p["errors"]+1), 180)
                penalize(idx, wait)
                other_alive = [x for j,x in enumerate(PROVIDERS)
                               if j != idx and not x["dead"]
                               and time.time() >= x["cooldown"]]
                if not other_alive:
                    sleep_t = min(wait, 60)
                    log(f"Pause {sleep_t}s (rien d'autre dispo)","TIME")
                    time.sleep(sleep_t)

            elif e.code == 403:
                body_low = body.lower()
                if any(w in body_low for w in ["denied","banned","suspended","permission"]):
                    penalize(idx, 0, dead=True)
                else:
                    penalize(idx, 300)

            elif e.code == 404:
                penalize(idx, 0, dead=True)

            elif e.code == 500:
                penalize(idx, 30)
                time.sleep(10)

            elif e.code == 503:
                penalize(idx, 60)
                time.sleep(20)

            else:
                penalize(idx, 20)
                time.sleep(5)

        except TimeoutError:
            log(f"[{tag}] TIMEOUT {timeout}s","WARN")
            penalize(idx, 30)

        except Exception as ex:
            log(f"[{tag}] Exception: {ex}","ERROR")
            if DEBUG: traceback.print_exc()
            penalize(idx, 15)
            time.sleep(5)

    log(f"[{tag}] ÉCHEC total {max_attempts} attempts","ERROR")
    return None

def disc_raw(embeds):
    if not DISCORD_WH: return False
    payload = json.dumps({
        "username": f"MaxOS AI v{VERSION}",
        "embeds":   embeds[:10]
    }).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WH, data=payload,
        headers={"Content-Type":"application/json","User-Agent":"MaxOS-Bot"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status in (200,204)
    except Exception as ex:
        log(f"Discord err: {ex}","WARN")
        return False

def make_embed(title, desc, color, fields=None):
    alive  = len(providers_alive())
    total  = sum(1 for p in PROVIDERS if not p["dead"])
    tk     = sum(p["tokens"] for p in PROVIDERS)
    calls  = sum(p["calls"]  for p in PROVIDERS)
    cur    = next((p["model"][:18] for p in providers_alive()), "?")
    e = {
        "title":       str(title)[:256],
        "description": str(desc)[:4096],
        "color":       color,
        "timestamp":   datetime.utcnow().isoformat()+"Z",
        "footer": {"text": (
            f"v{VERSION} | {cur} | {alive}/{total} | "
            f"up {uptime()} | ~{tk}tk | {calls}c | RL:{GH_RATE['remaining']}"
        )}
    }
    if fields:
        e["fields"] = [
            {"name":   str(f.get("name",""))[:256],
             "value":  str(f.get("value","?"))[:1024],
             "inline": bool(f.get("inline",False))}
            for f in fields[:25]
        ]
    return e

def disc_log(title, desc, color=0x5865F2):
    DISC_BUFFER.append((title, desc, color))
    _flush_disc(False)

def _flush_disc(force=True):
    global DISC_LAST
    now = time.time()
    if not force and now - DISC_LAST < DISC_INTERVAL:
        return
    if not DISC_BUFFER:
        return
    embeds = []
    while DISC_BUFFER and len(embeds) < 10:
        t, d, c = DISC_BUFFER.pop(0)
        embeds.append(make_embed(t, d, c))
    if embeds:
        disc_raw(embeds)
        DISC_LAST = time.time()

def disc_force(title, desc, color=0x5865F2, fields=None):
    _flush_disc(True)
    disc_raw([make_embed(title, desc, color, fields)])

def disc_task_start(i, total, nom, prio, cat, desc):
    pct = int((i-1)/total*100)
    disc_force(
        f"🚀 [{i}/{total}] {nom[:55]}",
        f"```\n{pbar(pct)}\n```\n{desc[:180]}",
        0xFFA500,
        [{"name":"Priorité","value":prio,"inline":True},
         {"name":"Cat","value":cat,"inline":True},
         {"name":"Uptime","value":uptime(),"inline":True},
         {"name":"Providers","value":providers_summary()[:800],"inline":False}]
    )

def disc_task_ok(i, total, nom, sha, written, deleted, elapsed, fix_count):
    pct = int(i/total*100)
    fs  = "\n".join(f"`{f}`" for f in (written+deleted)[:8]) or "aucun"
    disc_force(
        f"✅ [{i}/{total}] {nom[:50]}" + (f" fix×{fix_count}" if fix_count else ""),
        f"```\n{pbar(pct)}\n```\nCommit: `{sha}`",
        0x00FF88,
        [{"name":"⏱️","value":f"{elapsed:.0f}s","inline":True},
         {"name":"📁","value":str(len(written+deleted)),"inline":True},
         {"name":"Fichiers","value":fs,"inline":False}]
    )

def disc_task_fail(i, total, nom, reason, errors, elapsed):
    es = "\n".join(f"• `{e[:80]}`" for e in errors[:5]) or "?"
    disc_force(
        f"❌ [{i}/{total}] {nom[:50]}",
        f"Raison: `{reason}` | `{elapsed:.0f}s`",
        0xFF4444,
        [{"name":"Erreurs","value":es[:900],"inline":False},
         {"name":"Providers","value":providers_summary()[:600],"inline":False}]
    )

def disc_build(ok, errs, elapsed):
    if ok:
        disc_log("🔨 Build ✅", f"OK en `{elapsed:.1f}s`", 0x00CC44)
    else:
        es = "\n".join(f"`{e[:75]}`" for e in errs[:5])
        disc_log(f"🔨 Build ❌ ({len(errs)} erreurs)", f"`{elapsed:.1f}s`\n{es}", 0xFF2200)

def gh_api(method, endpoint, data=None, raw_url=None, retry=3):
    if not GH_TOKEN: return None
    url     = raw_url or f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/{endpoint}"
    payload = json.dumps(data).encode() if data else None
    for attempt in range(1, retry+1):
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
                if rem: GH_RATE["remaining"] = int(rem)
                if rst: GH_RATE["reset"]     = int(rst)
                body = r.read().decode()
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as e:
            body = ""
            try: body = e.read().decode()[:300]
            except: pass
            log(f"GH {method} {endpoint} HTTP {e.code}: {body[:80]}","WARN")
            if e.code in (500,502,503,504) and attempt < retry:
                time.sleep(5*attempt); continue
            if e.code == 403 and "rate limit" in body.lower():
                wait = max(GH_RATE["reset"]-time.time()+5, 60)
                time.sleep(wait); continue
            return None
        except Exception as ex:
            log(f"GH {ex}","ERROR")
            if attempt < retry: time.sleep(3); continue
            return None
    return None

def gh_open_prs():
    r = gh_api("GET","pulls?state=open&per_page=20")
    return r if isinstance(r,list) else []

def gh_pr_files(num):
    r = gh_api("GET",f"pulls/{num}/files?per_page=50")
    return r if isinstance(r,list) else []

def gh_pr_reviews(num):
    r = gh_api("GET",f"pulls/{num}/reviews")
    return r if isinstance(r,list) else []

def gh_comment(num, body):
    gh_api("POST",f"issues/{num}/comments",{"body":body})

def gh_post_review(num, body, event="COMMENT"):
    return gh_api("POST",f"pulls/{num}/reviews",{"body":body,"event":event})

def gh_open_issues():
    r = gh_api("GET","issues?state=open&per_page=30")
    if not isinstance(r,list): return []
    return [i for i in r if not i.get("pull_request")]

def gh_close_issue(num, reason="completed"):
    gh_api("PATCH",f"issues/{num}",{"state":"closed","state_reason":reason})

def gh_add_labels(num, labels):
    gh_api("POST",f"issues/{num}/labels",{"labels":labels})

def gh_list_labels():
    r = gh_api("GET","labels?per_page=100")
    return {l["name"]:l for l in (r if isinstance(r,list) else [])}

def gh_ensure_labels(desired):
    existing = gh_list_labels()
    count    = 0
    for name, color in desired.items():
        if name not in existing:
            gh_api("POST","labels",{"name":name,"color":color,"description":f"[AI] {name}"})
            count += 1
    return count

def gh_ensure_milestone(title):
    r = gh_api("GET","milestones?state=open&per_page=30")
    for m in (r if isinstance(r,list) else []):
        if m.get("title") == title: return m.get("number")
    r2 = gh_api("POST","milestones",{"title":title,"description":f"[MaxOS AI] {title}"})
    return r2.get("number") if r2 else None

def gh_list_releases(n=5):
    r = gh_api("GET",f"releases?per_page={n}")
    return r if isinstance(r,list) else []

def gh_create_release(tag, name, body, pre=False):
    r = gh_api("POST","releases",{
        "tag_name":tag,"name":name,"body":body,"draft":False,"prerelease":pre
    })
    return r.get("html_url") if r and "html_url" in r else None

def gh_issue_timeline(num):
    r = gh_api("GET",f"issues/{num}/timeline?per_page=50")
    return r if isinstance(r,list) else []

def gh_compare(base, head):
    r = gh_api("GET",f"compare/{base}...{head}")
    return r if r else {}

def git_cmd(args):
    r = subprocess.run(["git"]+args, cwd=REPO_PATH,
                       capture_output=True, text=True, timeout=60)
    return r.returncode==0, r.stdout, r.stderr

def git_push(task_name, files, description, model):
    if not files: return True, None, None
    dirs   = set(f.split("/")[0] for f in files if "/" in f)
    pmap   = {"kernel":"kernel","drivers":"driver","boot":"boot","ui":"ui","apps":"feat"}
    prefix = next((pmap[d] for d in pmap if d in dirs), "feat")
    fshort = ", ".join(os.path.basename(f) for f in files[:3])
    if len(files) > 3: fshort += f" +{len(files)-3}"
    short  = f"{prefix}: {task_name[:45]} [{fshort}]"
    msg    = f"{short}\n\nFiles: {', '.join(files)}\nModel: {model}\nArch: x86-32"
    git_cmd(["add","-A"])
    ok, out, err = git_cmd(["commit","-m",msg])
    if not ok:
        if "nothing to commit" in (out+err): return True, None, None
        log(f"Commit KO: {err[:200]}","ERROR"); return False, None, None
    _, sha, _ = git_cmd(["rev-parse","HEAD"])
    sha        = sha.strip()[:7]
    ok2, _, e2 = git_cmd(["push"])
    if not ok2:
        git_cmd(["pull","--rebase"])
        ok2, _, e2 = git_cmd(["push"])
        if not ok2:
            log(f"Push KO: {e2[:200]}","ERROR"); return False, None, None
    log(f"Push OK: {sha}","OK")
    return True, sha, short

BUILD_ERR_RE = re.compile(
    r"error:|fatal error:|fatal:|undefined reference|cannot find|no such file"
    r"|\*\*\* \[|Error \d+$|FAILED$|nasm:.*error|ld:.*error"
    r"|collect2: error|linker command failed|multiple definition",
    re.IGNORECASE
)

def parse_build_errors(log_text):
    seen, unique = set(), []
    for line in log_text.split("\n"):
        s = line.strip()
        if s and BUILD_ERR_RE.search(s) and s not in seen:
            seen.add(s); unique.append(s[:120])
    return unique[:20]

def make_build():
    subprocess.run(["make","clean"], cwd=REPO_PATH, capture_output=True, timeout=30)
    t0       = time.time()
    r        = subprocess.run(["make"], cwd=REPO_PATH,
                              capture_output=True, text=True, timeout=120)
    elapsed  = round(time.time()-t0, 1)
    ok       = r.returncode == 0
    log_text = r.stdout + r.stderr
    errs     = parse_build_errors(log_text)
    log(f"Build {'OK' if ok else 'FAIL'} {elapsed}s ({len(errs)} errs)","BUILD")
    for e in errs[:3]: log(f"  >> {e[:100]}","BUILD")
    disc_build(ok, errs, elapsed)
    return ok, log_text, errs

SKIP_DIRS  = {".git","build","__pycache__",".github","ai_dev"}
SKIP_FILES = {"screen.h.save"}
SRC_EXTS   = {".c",".h",".asm",".ld"}
ALL_FILES  = [
    "boot/boot.asm","kernel/kernel_entry.asm","kernel/kernel.c",
    "drivers/screen.h","drivers/screen.c","drivers/keyboard.h","drivers/keyboard.c",
    "ui/ui.h","ui/ui.c","apps/notepad.h","apps/notepad.c",
    "apps/terminal.h","apps/terminal.c","apps/sysinfo.h","apps/sysinfo.c",
    "apps/about.h","apps/about.c","Makefile","linker.ld",
]
STANDARD_LABELS = {
    "ai-reviewed":"0075ca","ai-approved":"0e8a16","ai-rejected":"b60205",
    "needs-fix":"e4e669","bug":"d73a4a","enhancement":"a2eeef","stale":"eeeeee",
    "kernel":"5319e7","driver":"1d76db","app":"0052cc",
}

OS_MISSION = "MISSION: OS bare metal x86. IDT+PIC→Timer PIT→Mémoire→VGA→Terminal→FAT12→GUI"

RULES = """RÈGLES BARE METAL x86:
INTERDIT: #include<stddef.h|string.h|stdlib.h|stdio.h|stdint.h|stdbool.h>
INTERDIT: size_t NULL bool true false uint32_t uint8_t malloc memset strlen printf
REMPLACE: size_t→unsigned int | NULL→0 | bool→int | true→1 | false→0 | uint32_t→unsigned int
GCC: -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie
ASM: nasm -f elf | LD: ld -m elf_i386 -T linker.ld --oformat binary
ZERO commentaire dans le code
kernel_entry.asm: label global _stack_top AVANT kernel_main
Nouveaux .c dans Makefile OBJS"""

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
    all_files = sorted(set(ALL_FILES + discover_files()))
    h = hashlib.md5()
    for f in all_files:
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p): h.update(str(os.path.getmtime(p)).encode())
    cur_hash = h.hexdigest()
    if not force and SOURCE_CACHE["hash"] == cur_hash and SOURCE_CACHE["data"]:
        return SOURCE_CACHE["data"]
    sources = {}
    for f in all_files:
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            try:
                with open(p,"r",encoding="utf-8",errors="ignore") as fh:
                    sources[f] = fh.read()
            except: sources[f] = None
        else:
            sources[f] = None
    SOURCE_CACHE.update({"hash": cur_hash, "data": sources})
    return sources

def build_context(sources, max_chars=36000):
    ctx  = "=== CODE SOURCE ===\n"
    for f,c in sources.items():
        ctx += f"{'[OK]' if c else '[--]'} {f}\n"
    ctx  += "\n"
    used  = len(ctx)
    prio  = ["kernel/kernel.c","kernel/kernel_entry.asm","Makefile","linker.ld",
             "drivers/screen.h","drivers/keyboard.h"]
    done  = set()
    for f in prio:
        c = sources.get(f,"")
        if not c: continue
        block = f"--- {f} ---\n{c}\n\n"
        if used+len(block) > max_chars: continue
        ctx += block; used += len(block); done.add(f)
    for f,c in sources.items():
        if f in done or not c: continue
        block = f"--- {f} ---\n{c}\n\n"
        if used+len(block) > max_chars: ctx += f"[{f} tronqué]\n"; continue
        ctx += block; used += len(block)
    return ctx

def proj_stats(sources):
    return {
        "files": sum(1 for c in sources.values() if c),
        "lines": sum(c.count("\n") for c in sources.values() if c),
        "chars": sum(len(c) for c in sources.values() if c),
    }

def analyze_quality(sources):
    bad_inc = ["stddef.h","string.h","stdlib.h","stdio.h","stdint.h","stdbool.h"]
    bad_sym = ["size_t","NULL","bool","true","false","uint32_t","uint8_t",
               "malloc","free","memset","memcpy","strlen","printf","sprintf"]
    viols = []
    c_f = asm_f = 0
    for fname, content in sources.items():
        if not content: continue
        if fname.endswith((".c",".h")):
            c_f += 1
            for i, line in enumerate(content.split("\n"), 1):
                s = line.strip()
                if s.startswith(("//","/*")): continue
                for inc in bad_inc:
                    if f"#include <{inc}>" in line or f'#include "{inc}"' in line:
                        viols.append(f"{fname}:{i} inc:{inc}")
                for sym in bad_sym:
                    if re.search(r'\b'+re.escape(sym)+r'\b', line):
                        viols.append(f"{fname}:{i} sym:{sym}"); break
        elif fname.endswith(".asm"):
            asm_f += 1
    return {"score": max(0,100-len(viols)*5), "violations": viols[:20],
            "c_files": c_f, "asm_files": asm_f}

def parse_ai_files(response):
    files, to_del = {}, []
    cur, lines, in_file = None, [], False
    for line in response.split("\n"):
        s = line.strip()
        if "=== FILE:" in s and s.endswith("==="):
            try:
                fname = s[s.index("=== FILE:")+9:s.rindex("===")].strip().strip("`").strip()
                if fname: cur=fname; lines=[]; in_file=True
            except: pass
            continue
        if s == "=== END FILE ===" and in_file:
            if cur:
                content = "\n".join(lines).strip()
                for lang in ["```c","```asm","```nasm","```makefile","```ld","```bash","```"]:
                    if content.startswith(lang):
                        content = content[len(lang):].lstrip("\n"); break
                if content.endswith("```"): content = content[:-3].rstrip("\n")
                if content.strip():
                    files[cur] = content.strip()
                    log(f"Parsé: {cur} ({len(content)} chars)")
            cur=None; lines=[]; in_file=False
            continue
        if "=== DELETE:" in s and s.endswith("==="):
            try:
                fname = s[s.index("=== DELETE:")+11:s.rindex("===")].strip()
                if fname: to_del.append(fname)
            except: pass
            continue
        if in_file: lines.append(line)
    if not files and not to_del:
        log(f"Parse: rien trouvé. Début: {response[:150]}","WARN")
    return files, to_del

def write_files(files):
    written = []
    for path, content in files.items():
        if path.startswith("/") or ".." in path: continue
        full = os.path.join(REPO_PATH, path)
        os.makedirs(os.path.dirname(full) or REPO_PATH, exist_ok=True)
        with open(full,"w",encoding="utf-8",newline="\n") as f:
            f.write(content)
        written.append(path); log(f"Écrit: {path}")
    SOURCE_CACHE["hash"] = None
    return written

def delete_files(paths):
    deleted = []
    for path in paths:
        if path.startswith("/") or ".." in path: continue
        full = os.path.join(REPO_PATH, path)
        if os.path.exists(full):
            os.remove(full); deleted.append(path); log(f"Del: {path}")
    SOURCE_CACHE["hash"] = None
    return deleted

def backup(paths):
    bak = {}
    for p in paths:
        full = os.path.join(REPO_PATH, p)
        if os.path.exists(full):
            with open(full,"r",encoding="utf-8",errors="ignore") as f:
                bak[p] = f.read()
    return bak

def restore(bak):
    for p,c in bak.items():
        full = os.path.join(REPO_PATH, p)
        os.makedirs(os.path.dirname(full) or REPO_PATH, exist_ok=True)
        with open(full,"w",encoding="utf-8",newline="\n") as f:
            f.write(c)
    if bak: log(f"Restauré {len(bak)} fichier(s)")
    SOURCE_CACHE["hash"] = None

def default_plan():
    return {
        "score_actuel": 30,
        "niveau_os": "Prototype bare metal",
        "fonctionnalites_presentes": ["Boot x86","VGA texte","Clavier","4 apps"],
        "fonctionnalites_manquantes_critiques": ["IDT","Timer PIT","Mémoire","VGA graphique"],
        "prochaine_milestone": "Kernel stable IDT+Timer",
        "plan_ameliorations": [
            {"nom":"IDT 256 + PIC 8259 + handlers","priorite":"CRITIQUE","categorie":"kernel",
             "fichiers_a_modifier":["kernel/kernel.c","kernel/kernel_entry.asm","Makefile"],
             "fichiers_a_creer":["kernel/idt.h","kernel/idt.c"],"fichiers_a_supprimer":[],
             "description":"kernel_entry.asm: global _stack_top avant kernel_main, pile 16KB. idt.h: IDTEntry packed IDTPtr. idt.c: idt_set_gate idt_init PIC 8259 remap IRQ0→0x20 IRQ8→0x28, stubs ASM 0-47, isr_handler irq_handler EOI, panic rouge. kernel.c: idt_init+sti.",
             "impact_attendu":"OS stable","complexite":"HAUTE"},
            {"nom":"Timer PIT 8253 100Hz + sleep_ms","priorite":"CRITIQUE","categorie":"kernel",
             "fichiers_a_modifier":["kernel/kernel.c","Makefile"],
             "fichiers_a_creer":["kernel/timer.h","kernel/timer.c"],"fichiers_a_supprimer":[],
             "description":"timer.h: timer_init() timer_ticks() sleep_ms(unsigned int). timer.c: PIT diviseur 11931 outb 0x43/0x40, volatile ticks, IRQ0 handler, uptime.",
             "impact_attendu":"Horloge système","complexite":"MOYENNE"},
            {"nom":"Terminal 20 commandes + historique","priorite":"HAUTE","categorie":"app",
             "fichiers_a_modifier":["apps/terminal.h","apps/terminal.c"],
             "fichiers_a_creer":[],"fichiers_a_supprimer":[],
             "description":"20 cmds: help ver mem uptime cls echo date reboot halt color beep calc about credits clear ps sysinfo license snake pong time. Historique 20 entrées flèche haut/bas. ZERO stdlib.",
             "impact_attendu":"Terminal complet","complexite":"MOYENNE"},
            {"nom":"Allocateur mémoire bitmap 4KB","priorite":"HAUTE","categorie":"kernel",
             "fichiers_a_modifier":["kernel/kernel.c","Makefile"],
             "fichiers_a_creer":["kernel/memory.h","kernel/memory.c"],"fichiers_a_supprimer":[],
             "description":"memory.h: mem_init(unsigned int,unsigned int) mem_alloc()→unsigned int mem_free(unsigned int) mem_used() mem_total(). bitmap[256] unsigned int 32MB/4KB. ZERO NULL→0.",
             "impact_attendu":"Allocation mémoire","complexite":"HAUTE"},
            {"nom":"VGA mode 13h 320x200 + desktop","priorite":"NORMALE","categorie":"driver",
             "fichiers_a_modifier":["drivers/screen.h","drivers/screen.c","kernel/kernel.c","Makefile"],
             "fichiers_a_creer":["drivers/vga.h","drivers/vga.c"],"fichiers_a_supprimer":[],
             "description":"vga.h: v_init() v_pixel(int,int,unsigned char) v_rect() v_fill() v_line(). vga.c: mode 13h 0xA0000, desktop bleu taskbar grise.",
             "impact_attendu":"Interface graphique","complexite":"HAUTE"},
        ]
    }

def phase_analyse(context, stats):
    log("=== PHASE 1: ANALYSE ===")
    disc_force("🔍 Analyse", f"`{stats['files']}` fichiers | `{stats['lines']}` lignes", 0x5865F2)
    prompt = (
        f"Expert OS bare metal x86.\n{RULES}\n{OS_MISSION}\n\n"
        f"{context}\n\nSTATS: {stats['files']} fichiers, {stats['lines']} lignes\n\n"
        "Retourne UNIQUEMENT ce JSON (rien d'autre):\n"
        '{"score_actuel":30,"niveau_os":"Prototype","fonctionnalites_presentes":["Boot"],'
        '"fonctionnalites_manquantes_critiques":["IDT"],'
        '"plan_ameliorations":[{"nom":"IDT","priorite":"CRITIQUE","categorie":"kernel",'
        '"fichiers_a_modifier":["kernel/kernel.c"],"fichiers_a_creer":["kernel/idt.h"],'
        '"fichiers_a_supprimer":[],"description":"specs","impact_attendu":"res","complexite":"HAUTE"}],'
        '"prochaine_milestone":"Kernel stable"}'
    )
    resp = ai_call(prompt, max_tokens=3000, timeout=60, tag="analyse")
    if not resp:
        log("Analyse KO → plan défaut","WARN")
        return default_plan()
    log(f"Analyse: {len(resp)} chars")
    clean = resp.strip()
    if clean.startswith("```"):
        lines = clean.split("\n")[1:]
        if lines and lines[-1].strip()=="```": lines=lines[:-1]
        clean = "\n".join(lines).strip()
    clean = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', clean)
    for _ in range(3):
        i = clean.find("{"); j = clean.rfind("}")+1
        if i >= 0 and j > i:
            try:
                result = json.loads(clean[i:j])
                log(f"Analyse OK: score={result.get('score_actuel','?')} "
                    f"{len(result.get('plan_ameliorations',[]))} tâches","OK")
                return result
            except json.JSONDecodeError as e:
                log(f"JSON err: {e}","WARN")
                clean = clean[i+1:]
    log("JSON KO → plan défaut","WARN")
    return default_plan()

def impl_prompt(task, ctx):
    return (
        f"{RULES}\n\n"
        f"TÂCHE: {task.get('nom','?')}\n"
        f"CAT: {task.get('categorie','?')} | CX: {task.get('complexite','?')}\n"
        f"MODIFIER: {task.get('fichiers_a_modifier',[])}\n"
        f"CRÉER: {task.get('fichiers_a_creer',[])}\n"
        f"SUPPRIMER: {task.get('fichiers_a_supprimer',[])}\n"
        f"SPECS: {task.get('description','')}\n\n"
        f"CODE EXISTANT:\n{ctx}\n\n"
        "OUTPUT:\n"
        "- Code 100% complet ZERO commentaire ZERO '...' ZERO placeholder\n"
        "- ZERO stdlib ZERO NULL→0 ZERO bool→int ZERO uint32_t→unsigned int\n"
        "- kernel_entry.asm: global _stack_top AVANT kernel_main\n"
        "- Nouveaux .c dans Makefile OBJS\n\n"
        "FORMAT STRICT:\n"
        "=== FILE: chemin/fichier.ext ===\n[code]\n=== END FILE ===\n\n"
        "GÉNÈRE MAINTENANT:"
    )

def task_context(task, sources):
    needed = set(task.get("fichiers_a_modifier",[])+task.get("fichiers_a_creer",[]))
    for f in list(needed):
        p = f.replace(".c",".h") if f.endswith(".c") else f.replace(".h",".c")
        if p in sources: needed.add(p)
    for e in ["kernel/kernel.c","kernel/kernel_entry.asm","Makefile","linker.ld","drivers/screen.h"]:
        needed.add(e)
    ctx = ""; used = 0
    for f in sorted(needed):
        c = sources.get(f,"")
        b = f"--- {f} ---\n{c if c else '[À CRÉER]'}\n\n"
        if used+len(b) > 18000: ctx += f"[{f} tronqué]\n"; continue
        ctx += b; used += len(b)
    return ctx

def auto_fix(build_log, errs, gen_files, bak, model, max_att=3):
    log(f"Auto-fix: {len(errs)} erreur(s)","BUILD")
    cur_log = build_log; cur_errs = errs
    for att in range(1, max_att+1):
        log(f"Fix {att}/{max_att}","BUILD")
        disc_log(f"🔧 Fix {att}/{max_att}", f"`{len(cur_errs)}` erreur(s)", 0x00AAFF)
        curr = {}
        for p in gen_files:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp):
                with open(fp,"r") as f: curr[p] = f.read()[:8000]
        ctx     = "".join(f"--- {p} ---\n{c}\n\n" for p,c in curr.items())
        err_str = "\n".join(cur_errs[:10])
        prompt  = (
            f"{RULES}\n\nERREURS:\n```\n{err_str}\n```\n\n"
            f"LOG:\n```\n{cur_log[-1000:]}\n```\n\n"
            f"FICHIERS:\n{ctx}\n\n"
            "CORRIGE TOUT. ZERO commentaire. ZERO stdlib. _stack_top global.\n"
            "FORMAT:\n=== FILE: fichier ===\n[code]\n=== END FILE ==="
        )
        resp = ai_call(prompt, max_tokens=24576, timeout=90, tag=f"fix/{att}")
        if not resp: continue
        files, _ = parse_ai_files(resp)
        if not files: log("Fix: rien parsé","WARN"); continue
        write_files(files)
        ok, cur_log, cur_errs = make_build()
        if ok:
            git_push("fix: corrections", list(files.keys()),
                     f"fix {len(errs)}→0", model)
            disc_force("🔧 Fix ✅", f"{len(errs)} err→0 en {att} att", 0x00AAFF)
            return True, {"attempts": att}
        log(f"Fix {att}: {len(cur_errs)} err restantes","WARN")
        time.sleep(5)
    restore(bak)
    return False, {"attempts": max_att}

def implement(task, sources, i, total):
    nom   = task.get("nom","?")
    cat   = task.get("categorie","?")
    cx    = task.get("complexite","MOYENNE")
    desc  = task.get("description","")
    f_mod = task.get("fichiers_a_modifier",[])
    f_new = task.get("fichiers_a_creer",[])
    model = next((p["model"] for p in providers_alive()), "?")

    log(f"\n{'='*50}\n[{i}/{total}] {nom}\n{'='*50}")
    disc_task_start(i, total, nom, task.get("priorite","?"), cat, desc)

    t0      = time.time()
    ctx     = task_context(task, sources)
    max_tok = {"HAUTE":32768,"MOYENNE":20480,"BASSE":12288}.get(cx, 20480)
    prompt  = impl_prompt(task, ctx)

    disc_log(f"⏳ [{nom[:35]}]",
             f"Prompt `{len(prompt):,}` chars | max `{max_tok}` tokens\n"
             f"Cibles: {', '.join(f'`{f}`' for f in (f_mod+f_new)[:4])}",
             0xFFA500)

    resp    = ai_call(prompt, max_tokens=max_tok, timeout=160, tag=f"impl/{nom[:16]}")
    elapsed = round(time.time()-t0, 1)

    if not resp:
        disc_task_fail(i, total, nom, "ai_fail", [], elapsed)
        return False, [], [], {"nom":nom,"elapsed":elapsed,"result":"ai_fail","errors":[]}

    files, to_del = parse_ai_files(resp)

    if not files and not to_del:
        disc_task_fail(i, total, nom, "parse_empty", [], elapsed)
        return False, [], [], {"nom":nom,"elapsed":elapsed,"result":"parse_empty","errors":[]}

    disc_log(f"📁 {len(files)} fichier(s)",
             "\n".join(f"`{f}` {len(c):,}c" for f,c in list(files.items())[:8]),
             0x00AAFF)

    bak_files = backup(list(files.keys()))
    written   = write_files(files)
    deleted   = delete_files(to_del)

    if not written and not deleted:
        disc_task_fail(i, total, nom, "no_files", [], elapsed)
        return False, [], [], {"nom":nom,"elapsed":elapsed,"result":"no_files","errors":[]}

    ok, build_log, errs = make_build()

    if ok:
        pushed, sha, _ = git_push(nom, written+deleted, desc, model)
        if pushed:
            m = {"nom":nom,"elapsed":round(time.time()-t0,1),"result":"success",
                 "sha":sha,"files":written+deleted,"model":model,"fix_count":0}
            disc_task_ok(i, total, nom, sha or "?", written, deleted, m["elapsed"], 0)
            return True, written, deleted, m
        restore(bak_files)
        disc_task_fail(i, total, nom, "push_fail", [], elapsed)
        return False, [], [], {"nom":nom,"elapsed":elapsed,"result":"push_fail","errors":[]}

    fixed, fix_m = auto_fix(build_log, errs, list(files.keys()), bak_files, model)
    if fixed:
        m = {"nom":nom,"elapsed":round(time.time()-t0,1),"result":"success_after_fix",
             "files":written+deleted,"model":model,"fix_count":fix_m.get("attempts",0),"sha":"fixed"}
        disc_task_ok(i, total, nom, "fixed", written, deleted, m["elapsed"], m["fix_count"])
        return True, written, deleted, m

    restore(bak_files)
    for p in written:
        if p not in bak_files:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp): os.remove(fp)
    SOURCE_CACHE["hash"] = None
    disc_task_fail(i, total, nom, "build_fail", errs, round(time.time()-t0,1))
    return False, [], [], {"nom":nom,"elapsed":round(time.time()-t0,1),
                           "result":"build_fail","errors":errs[:5]}

def handle_issues():
    issues = gh_open_issues()
    if not issues: log("Issues: aucune"); return
    log(f"Issues: {len(issues)}")
    bot_logins = {"MaxOS-AI-Bot","github-actions[bot]"}
    for issue in issues[:8]:
        num    = issue.get("number")
        title  = issue.get("title","")
        author = issue.get("user",{}).get("login","")
        if author in bot_logins: continue
        tl = gh_issue_timeline(num)
        if any(e.get("actor",{}).get("login","") in bot_logins or
               e.get("user",{}).get("login","") in bot_logins
               for e in (tl or [])): continue
        log(f"Issue #{num}: {title[:50]}")
        prompt = (
            f"Bot issues OS bare metal x86.\n"
            f"ISSUE #{num}: {title}\nAuteur: {author}\n"
            f"Corps: {(issue.get('body','') or '')[:500]}\n\n"
            "JSON UNIQUEMENT:\n"
            '{"type":"bug|enhancement|question|invalid","labels":["bug"],'
            '"action":"respond|close|label_only","close_reason":"completed|not_planned",'
            '"response":"réponse courte utile en français"}'
        )
        resp = ai_call(prompt, max_tokens=600, timeout=30, tag=f"issue/{num}")
        if not resp: continue
        clean = resp.strip()
        if clean.startswith("```"):
            ls = clean.split("\n")[1:]
            if ls and ls[-1].strip()=="```": ls=ls[:-1]
            clean = "\n".join(ls).strip()
        try:
            i = clean.find("{"); j = clean.rfind("}")+1
            if i >= 0 and j > i:
                a      = json.loads(clean[i:j])
                action = a.get("action","label_only")
                labels = [l for l in a.get("labels",[]) if l in STANDARD_LABELS]
                resp_t = a.get("response","")
                itype  = a.get("type","?")
                if labels: gh_add_labels(num, labels)
                if resp_t and action in ("respond","close","close_not_planned"):
                    icon = {"bug":"🐛","enhancement":"✨","question":"❓"}.get(itype,"💬")
                    gh_comment(num,
                        f"{icon} **MaxOS AI** — Réponse automatique\n\n{resp_t}\n\n"
                        f"---\n*MaxOS AI v{VERSION}*")
                if action == "close":             gh_close_issue(num,"completed")
                elif action == "close_not_planned": gh_close_issue(num,"not_planned")
                disc_log(f"🎫 Issue #{num}", f"**{title[:40]}** `{itype}` `{action}`", 0x00FF88)
        except Exception as ex:
            log(f"Issue #{num} err: {ex}","WARN")
        time.sleep(1)

def handle_stale(days_stale=21, days_close=7):
    issues = gh_open_issues()
    now    = time.time()
    for issue in issues:
        num      = issue.get("number")
        updated  = issue.get("updated_at","")
        labels   = [l.get("name","") for l in issue.get("labels",[])]
        is_stale = "stale" in labels
        try: updated_ts = datetime.strptime(updated,"%Y-%m-%dT%H:%M:%SZ").timestamp()
        except: continue
        age = now - updated_ts
        if age >= (days_stale+days_close)*86400 and is_stale:
            gh_comment(num,"🤖 **MaxOS AI**: Issue fermée (inactive). Rouvrez si besoin.")
            gh_close_issue(num,"not_planned")
        elif age >= days_stale*86400 and not is_stale:
            gh_add_labels(num,["stale"])
            gh_comment(num,
                f"⏰ **MaxOS AI**: Inactive {int(age/86400)} jours. "
                f"Fermeture dans **{days_close} jours**.")

def handle_prs():
    prs = gh_open_prs()
    if not prs: log("PRs: aucune"); return
    bot_logins = {"MaxOS-AI-Bot","github-actions[bot]"}
    for pr in prs[:4]:
        num    = pr.get("number")
        title  = pr.get("title","")
        author = pr.get("user",{}).get("login","")
        if author in bot_logins: continue
        if any(r.get("user",{}).get("login","") in bot_logins
               for r in (gh_pr_reviews(num) or [])): continue
        files_data = gh_pr_files(num)
        file_list  = "\n".join(
            f"- {f.get('filename','?')} (+{f.get('additions',0)}-{f.get('deletions',0)})"
            for f in files_data[:12]
        )
        patches = "".join(
            f"--- {f.get('filename','?')} ---\n{f.get('patch','')[:600]}\n"
            for f in [x for x in files_data
                      if any(x.get("filename","").endswith(e)
                             for e in [".c",".h",".asm"])][:4]
        )
        prompt = (
            f"Expert OS bare metal x86. Review PR.\n{RULES}\n\n"
            f"PR #{num}: {title}\nAuteur: {author}\n"
            f"Fichiers:\n{file_list}\nChangements:\n{patches}\n\n"
            "JSON UNIQUEMENT:\n"
            '{"decision":"APPROVE|REQUEST_CHANGES|COMMENT",'
            '"summary":"2 phrases","problems":["p1"],"positives":["p1"],'
            '"merge_safe":false,"violations":["v1"]}'
        )
        resp = ai_call(prompt, max_tokens=1200, timeout=40, tag=f"pr/{num}")
        if not resp: continue
        clean = resp.strip()
        if clean.startswith("```"):
            ls = clean.split("\n")[1:]
            if ls and ls[-1].strip()=="```": ls=ls[:-1]
            clean = "\n".join(ls).strip()
        try:
            i = clean.find("{"); j = clean.rfind("}")+1
            if i >= 0 and j > i:
                a          = json.loads(clean[i:j])
                decision   = a.get("decision","COMMENT")
                merge_safe = a.get("merge_safe",False)
                icon       = {"APPROVE":"✅","REQUEST_CHANGES":"🔴","COMMENT":"💬"}.get(decision,"💬")
                body       = (
                    f"## {icon} Code Review MaxOS AI — PR #{num}\n\n"
                    f"> **{decision}** | Safe: {'🟢' if merge_safe else '🔴'}\n\n"
                    f"{a.get('summary','')}\n\n"
                )
                if a.get("problems"):   body += "### ❌\n" + "\n".join(f"- {p}" for p in a["problems"])+"\n\n"
                if a.get("positives"):  body += "### ✅\n"  + "\n".join(f"- {p}" for p in a["positives"])+"\n\n"
                if a.get("violations"): body += "### ⚠️\n"+ "\n".join(f"- `{v}`" for v in a["violations"])+"\n\n"
                body += f"---\n*MaxOS AI v{VERSION}*"
                event = ("APPROVE" if decision=="APPROVE" and merge_safe else
                         "REQUEST_CHANGES" if decision=="REQUEST_CHANGES" else "COMMENT")
                gh_post_review(num, body, event)
                labels_map = {"APPROVE":["ai-approved","ai-reviewed"],
                              "REQUEST_CHANGES":["ai-rejected","ai-reviewed","needs-fix"],
                              "COMMENT":["ai-reviewed"]}
                gh_add_labels(num, labels_map.get(decision,["ai-reviewed"]))
                disc_log(f"📋 PR #{num} {decision}",
                         f"**{title[:45]}** Safe:{'✅' if merge_safe else '❌'}",
                         0x00AAFF if decision=="APPROVE" else 0xFF4444 if decision=="REQUEST_CHANGES" else 0xFFA500)
        except Exception as ex:
            log(f"PR #{num} err: {ex}","WARN")
        time.sleep(1.5)

def create_release(tasks_done, tasks_failed, analyse, stats):
    releases = gh_list_releases()
    last_tag = "v0.0.0"
    for r in releases:
        tag = r.get("tag_name","")
        if re.match(r"v\d+\.\d+\.\d+",tag): last_tag=tag; break
    try:
        parts = last_tag.lstrip("v").split(".")
        major, minor, patch = int(parts[0]),int(parts[1]),int(parts[2])
    except: major, minor, patch = 0,0,0
    score = analyse.get("score_actuel",30)
    if score >= 70: minor += 1; patch = 0
    else: patch += 1
    new_tag  = f"v{major}.{minor}.{patch}"
    niveau   = analyse.get("niveau_os","?")
    ms       = analyse.get("prochaine_milestone","?")
    feats    = analyse.get("fonctionnalites_presentes",[])
    feat_txt = "\n".join(f"- ✅ {f}" for f in feats[:8]) or "- (Aucune)"
    changes  = "".join(
        f"- ✅ {t.get('nom','?')[:55]} [`{t.get('sha','?')}`] ({t.get('model','?')})"
        + (f" fix×{t.get('fix_count',0)}" if t.get("fix_count") else "") + "\n"
        for t in tasks_done
    ) or "- Maintenance\n"
    failed_s = ("\n## ⏭️ Reporté\n\n"+"\n".join(f"- ❌ {n}" for n in tasks_failed)+"\n") if tasks_failed else ""
    tk       = sum(p["tokens"] for p in PROVIDERS)
    calls    = sum(p["calls"]  for p in PROVIDERS)
    types    = ", ".join(sorted(set(p["type"] for p in PROVIDERS if p["calls"]>0))) or "gemini"
    now      = datetime.utcnow()
    body     = (
        f"# MaxOS {new_tag}\n\n"
        f"| | |\n|---|---|\n"
        f"| Score | **{score}/100** |\n| Niveau | {niveau} |\n"
        f"| Fichiers | {stats.get('files',0)} |\n| Lignes | {stats.get('lines',0)} |\n"
        f"| Milestone | {ms} |\n\n"
        f"## ✅ Changements\n\n{changes}{failed_s}\n"
        f"## 🧩 Fonctionnalités\n\n{feat_txt}\n\n"
        f"---\n## ⚙️\n| IA | {types} | Appels | {calls} | ~Tokens | {tk} |\n\n"
        f"```bash\nqemu-system-i386 -drive format=raw,file=os.img,if=floppy -boot a -vga std -k fr -m 32\n```\n\n"
        f"*MaxOS AI v{VERSION} | {now.strftime('%Y-%m-%d %H:%M')} UTC*\n"
    )
    url = gh_create_release(new_tag,
                            f"MaxOS {new_tag} | {niveau} | {now.strftime('%Y-%m-%d')}",
                            body, pre=(score<50))
    if url:
        disc_force("🚀 Release",f"**{new_tag}** | {score}/100",0x00FF88,
                   [{"name":"Version","value":new_tag,"inline":True},
                    {"name":"Score","value":f"{score}/100","inline":True},
                    {"name":"Lien","value":f"[Release]({url})","inline":False}])
        log(f"Release {new_tag} → {url}","OK")
    return url

def final_report(success, total, tasks_done, tasks_failed, analyse, stats):
    score  = analyse.get("score_actuel",30)
    niveau = analyse.get("niveau_os","?")
    pct    = int(success/total*100) if total > 0 else 0
    color  = 0x00FF88 if pct>=80 else 0xFFA500 if pct>=50 else 0xFF4444
    elapsed= round(time.time()-START_TIME, 0)
    tk     = sum(p["tokens"] for p in PROVIDERS)
    calls  = sum(p["calls"]  for p in PROVIDERS)
    sources= read_all()
    qual   = analyze_quality(sources)
    done_s = "\n".join(f"✅ {t.get('nom','?')[:38]} ({t.get('elapsed',0):.0f}s)" for t in tasks_done) or "Aucune"
    fail_s = "\n".join(f"❌ {n[:38]}" for n in tasks_failed) or "Aucune"
    disc_force(
        f"🏁 Cycle — {success}/{total} réussies",
        f"```\n{pbar(pct)}\n```",
        color,
        [{"name":"✅ Succès","value":str(success),"inline":True},
         {"name":"❌ Échecs","value":str(total-success),"inline":True},
         {"name":"📈 Taux","value":f"{pct}%","inline":True},
         {"name":"⏱️ Durée","value":f"{int(elapsed)}s","inline":True},
         {"name":"🔑 Appels","value":str(calls),"inline":True},
         {"name":"💬 ~Tokens","value":str(tk),"inline":True},
         {"name":"📊 Qualité","value":f"{qual['score']}/100","inline":True},
         {"name":"📁 Fichiers","value":str(stats.get("files",0)),"inline":True},
         {"name":"📝 Lignes","value":str(stats.get("lines",0)),"inline":True},
         {"name":"📊 Score OS","value":f"{score}/100 {niveau}","inline":False},
         {"name":"✅ Réussies","value":done_s[:800],"inline":False},
         {"name":"❌ Échouées","value":fail_s[:400],"inline":False},
         {"name":"🔑 Providers","value":providers_summary()[:700],"inline":False}]
    )
    if qual["violations"]:
        disc_force("⚠️ Violations",
                   "```\n"+"\n".join(f"• {v}" for v in qual["violations"][:10])+"\n```",
                   0xFF6600)

def main():
    print("="*55)
    print(f"  MaxOS AI Developer v{VERSION}")
    by_type = {}
    for p in PROVIDERS:
        by_type.setdefault(p["type"],[]).append(p)
    for t, ps in by_type.items():
        keys_uniq = set(p["key"][:8] for p in ps)
        models_uniq = set(p["model"] for p in ps)
        print(f"  {t:12}: {len(keys_uniq)} clé(s) × {len(models_uniq)} modèle(s) = {len(ps)} providers")
    print(f"  Total: {len(PROVIDERS)} providers")
    print("="*55)

    if not PROVIDERS:
        print("FATAL: Aucun provider. Vérifie les secrets GitHub.")
        sys.exit(1)

    disc_force(
        f"🤖 MaxOS AI v{VERSION} démarré",
        f"`{len(PROVIDERS)}` providers | Multi-API",
        0x5865F2,
        [{"name":"Providers","value":providers_summary()[:900],"inline":False},
         {"name":"Repo","value":f"{REPO_OWNER}/{REPO_NAME}","inline":True},
         {"name":"Mode","value":"Multi-provider anti-429","inline":True}]
    )

    subprocess.run(["make","clean"], cwd=REPO_PATH, capture_output=True, timeout=30)

    gh_ensure_labels(STANDARD_LABELS)
    handle_issues()
    if not watchdog(): sys.exit(0)
    handle_stale()
    handle_prs()
    if not watchdog(): sys.exit(0)

    sources = read_all(force=True)
    stats   = proj_stats(sources)
    qual    = analyze_quality(sources)
    log(f"Sources: {stats['files']} fichiers, {stats['lines']} lignes")

    disc_force("📊 Sources",
               f"`{stats['files']}` fichiers | `{stats['lines']}` lignes",
               0x5865F2,
               [{"name":"Qualité","value":f"{qual['score']}/100 ({len(qual['violations'])} violations)","inline":True},
                {"name":".c","value":str(qual.get("c_files",0)),"inline":True},
                {"name":".asm","value":str(qual.get("asm_files",0)),"inline":True}])

    analyse  = phase_analyse(build_context(sources), stats)
    score    = analyse.get("score_actuel",30)
    niveau   = analyse.get("niveau_os","?")
    plan     = analyse.get("plan_ameliorations",[])
    milestone= analyse.get("prochaine_milestone","?")
    features = analyse.get("fonctionnalites_presentes",[])
    manques  = analyse.get("fonctionnalites_manquantes_critiques",[])

    order = {"CRITIQUE":0,"HAUTE":1,"NORMALE":2,"BASSE":3}
    plan  = sorted(plan, key=lambda t: order.get(t.get("priorite","NORMALE"),2))

    log(f"Score={score} | {niveau} | {len(plan)} tâches","OK")

    if milestone:
        ms_num = gh_ensure_milestone(milestone)
        if ms_num: log(f"Milestone '{milestone}' = #{ms_num}")

    disc_force(
        f"📊 Score {score}/100 — {niveau}",
        f"```\n{pbar(score)}\n```",
        0x00AAFF if score>=60 else 0xFFA500 if score>=30 else 0xFF4444,
        [{"name":"✅ Présentes","value":"\n".join(f"+ {f}" for f in features[:5]) or "?","inline":True},
         {"name":"❌ Manquantes","value":"\n".join(f"- {f}" for f in manques[:5]) or "?","inline":True},
         {"name":"📋 Plan","value":"\n".join(
             f"[{i+1}] `{t.get('priorite','?')}` {t.get('nom','?')[:30]}"
             for i,t in enumerate(plan[:6])
         ),"inline":False},
         {"name":"🎯 Milestone","value":milestone[:80],"inline":True},
         {"name":"🔑 Providers","value":providers_summary()[:500],"inline":False}]
    )

    total        = len(plan)
    success      = 0
    tasks_done   = []
    tasks_failed = []

    for i, task in enumerate(plan, 1):
        if not watchdog(): break
        disc_log(f"💓 Heartbeat [{i}/{total}]",
                 f"Prochaine: **{task.get('nom','?')[:45]}**\n{providers_summary()[:400]}",
                 0x7289DA)
        sources_now = read_all()
        ok, written, deleted, metrics = implement(task, sources_now, i, total)
        TASK_METRICS.append(metrics)
        if ok:
            success += 1
            tasks_done.append(metrics)
        else:
            tasks_failed.append(task.get("nom","?"))
        if i < total:
            n_ok  = len(providers_alive())
            pause = 5 if n_ok >= 3 else 10 if n_ok >= 1 else 20
            log(f"Pause {pause}s ({n_ok} providers dispo)")
            _flush_disc(True)
            time.sleep(pause)

    if success > 0:
        sources_f = read_all(force=True)
        create_release(tasks_done, tasks_failed, analyse, proj_stats(sources_f))

    sources_f = read_all(force=True)
    final_report(success, total, tasks_done, tasks_failed, analyse, proj_stats(sources_f))
    _flush_disc(True)

    print(f"\n[FIN] {success}/{total} | {uptime()} | RL:{GH_RATE['remaining']}")
    for t in tasks_done:   print(f"  ✅ {t.get('nom','?')[:50]} ({t.get('elapsed',0):.0f}s)")
    for n in tasks_failed: print(f"  ❌ {n[:50]}")

if __name__ == "__main__":
    main()
