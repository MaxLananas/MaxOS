#!/usr/bin/env python3
import os, sys, json, time, subprocess, re, hashlib, traceback
import urllib.request, urllib.error
from datetime import datetime, timezone

VERSION    = "12.0"
DEBUG      = os.environ.get("MAXOS_DEBUG","0") == "1"
START_TIME = time.time()
MAX_RUNTIME = 3200

def _env(key, default=""):
    return os.environ.get(key, default)

REPO_OWNER  = _env("REPO_OWNER","MaxLananas")
REPO_NAME   = _env("REPO_NAME","MaxOS")
REPO_PATH   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GH_TOKEN    = _env("GH_PAT") or _env("GITHUB_TOKEN")
DISCORD_WH  = _env("DISCORD_WEBHOOK")

def load_providers():
    providers = []

    gemini_models = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-flash-8b",
    ]
    for i in range(1, 15):
        suffix = "" if i == 1 else f"_{i}"
        key    = _env(f"GEMINI_API_KEY{suffix}")
        if key:
            for model in gemini_models:
                providers.append({
                    "type":    "gemini",
                    "id":      f"gemini_{i}_{model}",
                    "key":     key,
                    "model":   model,
                    "url":     (f"https://generativelanguage.googleapis.com/v1beta"
                                f"/models/{model}:generateContent?key={key}"),
                    "rpm":     15,
                    "tpm":     1000000,
                    "cooldown": 0,
                    "errors":   0,
                    "calls":    0,
                    "tokens":   0,
                    "forbidden": False,
                })

    for i in range(1, 10):
        suffix = "" if i == 1 else f"_{i}"
        key    = _env(f"OPENROUTER_KEY{suffix}")
        if not key: continue
        for model in [
            "google/gemini-2.0-flash-exp:free",
            "qwen/qwen-2.5-coder-32b-instruct:free",
            "deepseek/deepseek-r1-distill-llama-70b:free",
            "meta-llama/llama-3.1-8b-instruct:free",
            "google/gemini-flash-1.5-8b:free",
        ]:
            providers.append({
                "type":    "openrouter",
                "id":      f"or_{i}_{model.split('/')[1][:15]}",
                "key":     key,
                "model":   model,
                "url":     "https://openrouter.ai/api/v1/chat/completions",
                "rpm":     20,
                "tpm":     500000,
                "cooldown": 0,
                "errors":   0,
                "calls":    0,
                "tokens":   0,
                "forbidden": False,
            })

    for i in range(1, 10):
        suffix = "" if i == 1 else f"_{i}"
        key    = _env(f"GROQ_KEY{suffix}")
        if not key: continue
        for model in [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "gemma2-9b-it",
        ]:
            providers.append({
                "type":    "groq",
                "id":      f"groq_{i}_{model[:15]}",
                "key":     key,
                "model":   model,
                "url":     "https://api.groq.com/openai/v1/chat/completions",
                "rpm":     30,
                "tpm":     6000,
                "cooldown": 0,
                "errors":   0,
                "calls":    0,
                "tokens":   0,
                "forbidden": False,
            })

    for i in range(1, 5):
        suffix = "" if i == 1 else f"_{i}"
        key    = _env(f"MISTRAL_KEY{suffix}")
        if not key: continue
        providers.append({
            "type":    "mistral",
            "id":      f"mistral_{i}",
            "key":     key,
            "model":   "mistral-small-latest",
            "url":     "https://api.mistral.ai/v1/chat/completions",
            "rpm":     5,
            "tpm":     500000,
            "cooldown": 0,
            "errors":   0,
            "calls":    0,
            "tokens":   0,
            "forbidden": False,
        })

    return providers

PROVIDERS  = load_providers()
PROV_IDX   = 0

GH_RATE    = {"remaining": 5000, "reset": 0}
SOURCE_CACHE = {"hash": None, "data": None}
TASK_METRICS = []
DISC_BUFFER  = []
DISC_LAST    = 0
DISC_INTERVAL = 25

def ts():
    return datetime.now(timezone.utc).strftime("%H:%M:%S")

def uptime():
    s = int(time.time() - START_TIME)
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def log(msg, level="INFO"):
    icons = {
        "INFO":"📋","WARN":"⚠️","ERROR":"❌","OK":"✅",
        "BUILD":"🔨","GEM":"🤖","GIT":"📦","NET":"🌐","TIME":"⏱️"
    }
    print(f"[{ts()}] {icons.get(level,'📋')} {msg}", flush=True)

def pbar(pct, w=22):
    f = int(w * pct / 100)
    return "█"*f + "░"*(w-f) + f" {pct}%"

def mask(k):
    return k[:6]+"***"+k[-4:] if len(k)>10 else "***"

def watchdog():
    if time.time() - START_TIME >= MAX_RUNTIME:
        log(f"Watchdog: {MAX_RUNTIME}s atteint","WARN")
        disc_force("⏰ Watchdog",f"Arrêt après {uptime()}",0xFFA500)
        return False
    return True

def providers_summary():
    now    = time.time()
    active = sum(1 for p in PROVIDERS if not p["forbidden"] and now >= p["cooldown"])
    total  = len(PROVIDERS)
    lines  = []
    seen   = set()
    for p in PROVIDERS:
        key_id = p["key"][:8]
        if key_id in seen: continue
        seen.add(key_id)
        st  = "🟢" if now >= p["cooldown"] else f"🔴CD+{int(p['cooldown']-now)}s"
        lines.append(f"{p['type']} {mask(p['key'])}: {st} | {p['calls']}c | ~{p['tokens']}tk")
    return f"{active}/{total} actifs\n" + "\n".join(lines[:8])

def get_provider():
    global PROV_IDX
    now = time.time()
    n   = len(PROVIDERS)
    for delta in range(n):
        idx = (PROV_IDX + delta) % n
        p   = PROVIDERS[idx]
        if not p["forbidden"] and now >= p["cooldown"]:
            PROV_IDX = idx
            return idx, p
    best_idx = min(range(n), key=lambda i: PROVIDERS[i]["cooldown"]
                   if not PROVIDERS[i]["forbidden"] else float("inf"))
    wait = PROVIDERS[best_idx]["cooldown"] - now + 1
    log(f"Tous providers en cooldown → attente {int(wait)}s","TIME")
    disc_force("⏳ Rate limit",
               f"Tous les providers en cooldown\nAttente: **{int(wait)}s** | Uptime: {uptime()}\n"
               f"{providers_summary()}",
               0xFF8800)
    time.sleep(max(wait, 1))
    PROV_IDX = best_idx
    return best_idx, PROVIDERS[best_idx]

def set_provider_cooldown(idx, secs, forbidden=False):
    p = PROVIDERS[idx]
    p["cooldown"] = time.time() + secs
    p["errors"]  += 1
    if forbidden:
        p["forbidden"] = True
        log(f"Provider {p['id']} blacklisté","WARN")
    else:
        log(f"Provider {p['id']} cooldown {secs}s","WARN")

def call_gemini(p, payload_bytes, timeout):
    req = urllib.request.Request(
        p["url"], data=payload_bytes,
        headers={"Content-Type":"application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def call_openai_compat(p, prompt, max_tokens, timeout):
    payload = json.dumps({
        "model":      p["model"],
        "messages":   [{"role":"user","content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.05,
    }).encode("utf-8")
    headers = {
        "Content-Type":  "application/json",
        "Authorization": "Bearer " + p["key"],
    }
    if p["type"] == "openrouter":
        headers["HTTP-Referer"] = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
        headers["X-Title"]      = "MaxOS AI Developer"
    req = urllib.request.Request(p["url"], data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def extract_gemini(data):
    try:
        cands = data.get("candidates",[])
        if not cands: return None
        c      = cands[0]
        finish = c.get("finishReason","STOP")
        if finish in ("SAFETY","RECITATION"): return None
        parts  = c.get("content",{}).get("parts",[])
        texts  = [p.get("text","") for p in parts
                  if isinstance(p,dict) and not p.get("thought") and p.get("text")]
        result = "".join(texts)
        return result if result else None
    except Exception:
        return None

def extract_openai(data):
    try:
        choices = data.get("choices",[])
        if not choices: return None
        msg = choices[0].get("message",{})
        return msg.get("content","") or None
    except Exception:
        return None

def gemini_payload(prompt, max_tokens):
    return json.dumps({
        "contents": [{"parts":[{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens,"temperature": 0.05}
    }).encode("utf-8")

def ai_call(prompt, max_tokens=32768, timeout=150, tag="?"):
    if len(prompt) > 55000:
        prompt = prompt[:55000] + "\n[TRONQUÉ]"

    gem_payload = gemini_payload(prompt, max_tokens)
    max_attempts = min(len(PROVIDERS) * 2, 20)

    for attempt in range(1, max_attempts+1):
        if not watchdog():
            return None

        idx, p = get_provider()
        log(f"[{tag}] {p['type']}/{p['id']} attempt={attempt}","GEM")
        disc_log(f"🤖 [{tag}] attempt {attempt}",
                 f"`{p['type']}` | `{p['model'][:30]}` | clé `{mask(p['key'])}`\n"
                 f"Uptime: `{uptime()}` | RL GitHub: `{GH_RATE['remaining']}`",
                 0x5865F2)

        try:
            t0 = time.time()
            if p["type"] == "gemini":
                data = call_gemini(p, gem_payload, timeout)
                text = extract_gemini(data)
            else:
                data = call_openai_compat(p, prompt, max_tokens, timeout)
                text = extract_openai(data)

            elapsed = round(time.time()-t0, 1)

            if text is None:
                log(f"[{tag}] Réponse vide ({p['id']})","WARN")
                set_provider_cooldown(idx, 30)
                continue

            est_tk = len(text)//4
            p["calls"]  += 1
            p["tokens"] += est_tk

            log(f"[{tag}] ✅ {len(text)} chars en {elapsed}s (~{est_tk}tk)","OK")
            disc_log(f"✅ [{tag}] OK",
                     f"`{len(text):,}` chars | `{elapsed}s` | ~`{est_tk}` tokens\n"
                     f"`{p['type']}` | `{p['model'][:30]}`",
                     0x00FF88)
            PROV_IDX_after = (idx+1) % len(PROVIDERS)
            globals()["PROV_IDX"] = PROV_IDX_after
            return text

        except urllib.error.HTTPError as e:
            elapsed = round(time.time()-t0, 1)
            body    = ""
            try: body = e.read().decode()[:300]
            except: pass
            log(f"[{tag}] HTTP {e.code} ({p['id']}) en {elapsed}s","WARN")
            disc_log(f"⚠️ [{tag}] HTTP {e.code}",
                     f"`{p['type']}` | `{p['model'][:25]}`\n"
                     f"Code: `{e.code}` | `{body[:150]}`",
                     0xFF4400)

            if e.code == 429:
                errs = p["errors"]
                wait = min(60*(errs+1), 180)
                set_provider_cooldown(idx, wait)
                now = time.time()
                has_other = any(
                    not PROVIDERS[i]["forbidden"] and now >= PROVIDERS[i]["cooldown"]
                    for i in range(len(PROVIDERS)) if i != idx
                )
                if not has_other:
                    sleep_t = min(wait, 60)
                    log(f"Pause {sleep_t}s (tous busy)","TIME")
                    time.sleep(sleep_t)

            elif e.code == 403:
                body_low = body.lower()
                if "denied" in body_low or "banned" in body_low or "suspended" in body_low:
                    set_provider_cooldown(idx, 9999, forbidden=True)
                else:
                    set_provider_cooldown(idx, 600)

            elif e.code in (400, 404):
                set_provider_cooldown(idx, 60)

            elif e.code == 500:
                set_provider_cooldown(idx, 30)
                time.sleep(15)

            else:
                set_provider_cooldown(idx, 30)
                time.sleep(10)

        except TimeoutError:
            log(f"[{tag}] TIMEOUT {timeout}s ({p['id']})","WARN")
            set_provider_cooldown(idx, 20)

        except Exception as ex:
            log(f"[{tag}] Exception: {ex}","ERROR")
            if DEBUG: traceback.print_exc()
            set_provider_cooldown(idx, 15)
            time.sleep(8)

    log(f"[{tag}] ÉCHEC total après {max_attempts} attempts","ERROR")
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
        log(f"Discord: {ex}","WARN")
        return False

def make_embed(title, desc, color, fields=None):
    now    = time.time()
    active = sum(1 for p in PROVIDERS if not p["forbidden"] and now >= p["cooldown"])
    total  = len(PROVIDERS)
    total_tokens = sum(p["tokens"] for p in PROVIDERS)
    total_calls  = sum(p["calls"]  for p in PROVIDERS)
    cur_model = next(
        (p["model"][:20] for p in PROVIDERS
         if not p["forbidden"] and now >= p["cooldown"]),
        "?"
    )
    e = {
        "title":       str(title)[:256],
        "description": str(desc)[:4096],
        "color":       color,
        "timestamp":   datetime.utcnow().isoformat()+"Z",
        "footer": {"text": (
            f"v{VERSION} | {cur_model} | {active}/{total} providers | "
            f"uptime {uptime()} | ~{total_tokens}tk | {total_calls}calls | RL:{GH_RATE['remaining']}"
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
    flush_disc(force=False)

def flush_disc(force=True):
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
    flush_disc(force=True)
    disc_raw([make_embed(title, desc, color, fields)])

def disc_task_start(i, total, nom, priorite, cat, desc):
    pct = int((i-1)/total*100)
    disc_force(
        f"🚀 [{i}/{total}] {nom[:55]}",
        f"```\n{pbar(pct)}\n```\n{desc[:180]}",
        0xFFA500,
        [{"name":"Priorité","value":priorite,"inline":True},
         {"name":"Cat","value":cat,"inline":True},
         {"name":"Uptime","value":uptime(),"inline":True},
         {"name":"Providers","value":providers_summary()[:900],"inline":False}]
    )

def disc_task_ok(i, total, nom, sha, written, deleted, elapsed, fix_count):
    pct      = int(i/total*100)
    files_str = "\n".join(f"`{f}`" for f in (written+deleted)[:8]) or "aucun"
    disc_force(
        f"✅ [{i}/{total}] {nom[:50]}" + (f" (fix×{fix_count})" if fix_count else ""),
        f"```\n{pbar(pct)}\n```\nCommit: `{sha}`",
        0x00FF88,
        [{"name":"⏱️ Temps","value":f"{elapsed:.0f}s","inline":True},
         {"name":"📁 Fichiers","value":str(len(written+deleted)),"inline":True},
         {"name":"📝 Modifiés","value":files_str,"inline":False}]
    )

def disc_task_fail(i, total, nom, reason, errors, elapsed):
    errs_str = "\n".join(f"• `{e[:80]}`" for e in errors[:5]) or "?"
    disc_force(
        f"❌ [{i}/{total}] {nom[:50]}",
        f"Raison: `{reason}` | `{elapsed:.0f}s`",
        0xFF4444,
        [{"name":"🔴 Erreurs","value":errs_str[:900],"inline":False},
         {"name":"Providers","value":providers_summary()[:600],"inline":False}]
    )

def disc_build(ok, errs, elapsed):
    if ok:
        disc_log("🔨 Build ✅",f"Compilation OK en `{elapsed:.1f}s`",0x00CC44)
    else:
        err_str = "\n".join(f"• `{e[:80]}`" for e in errs[:6])
        disc_log(f"🔨 Build ❌ ({len(errs)} erreur(s))",
                 f"`{elapsed:.1f}s`\n{err_str}",0xFF2200)

def disc_heartbeat(task_i, total, msg):
    disc_log(f"💓 Heartbeat [{task_i}/{total}]",
             f"{msg}\nUptime: `{uptime()}`\n{providers_summary()[:500]}",
             0x7289DA)

def gh_api(method, endpoint, data=None, raw_url=None, retry=3):
    if not GH_TOKEN: return None
    url     = raw_url or f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/{endpoint}"
    payload = json.dumps(data).encode() if data else None
    for attempt in range(1, retry+1):
        req = urllib.request.Request(
            url, data=payload,
            headers={
                "Authorization":        "Bearer "+GH_TOKEN,
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
            log(f"GitHub {method} {endpoint} HTTP {e.code}: {body[:80]}","WARN")
            if e.code in (500,502,503,504) and attempt < retry:
                time.sleep(5*attempt); continue
            if e.code == 403 and "rate limit" in body.lower():
                wait = max(GH_RATE["reset"]-time.time()+5, 60)
                log(f"GitHub rate limit → {int(wait)}s","WARN")
                time.sleep(wait); continue
            return None
        except Exception as ex:
            log(f"GitHub {ex}","ERROR")
            if attempt < retry: time.sleep(3); continue
            return None
    return None

def gh_open_prs():
    r = gh_api("GET","pulls?state=open&per_page=20")
    return r if isinstance(r,list) else []

def gh_pr_files(num):
    r = gh_api("GET",f"pulls/{num}/files?per_page=50")
    return r if isinstance(r,list) else []

def gh_pr_commits(num):
    r = gh_api("GET",f"pulls/{num}/commits?per_page=50")
    return r if isinstance(r,list) else []

def gh_pr_reviews(num):
    r = gh_api("GET",f"pulls/{num}/reviews")
    return r if isinstance(r,list) else []

def gh_comment(num, body):
    gh_api("POST",f"issues/{num}/comments",{"body":body})

def gh_post_review(num, body, event="COMMENT", comments=None):
    payload = {"body":body,"event":event}
    if comments:
        payload["comments"] = [
            {"path":c.get("path",""),"line":c.get("line",1),"side":"RIGHT","body":c.get("body","")}
            for c in comments if c.get("path") and c.get("body")
        ]
    return gh_api("POST",f"pulls/{num}/reviews",payload)

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
            gh_api("POST","labels",{"name":name,"color":color,
                                    "description":f"[MaxOS AI] {name}"})
            log(f"Label créé: {name}")
            count += 1
    return count

def gh_list_milestones():
    r = gh_api("GET","milestones?state=open&per_page=30")
    return r if isinstance(r,list) else []

def gh_ensure_milestone(title):
    for m in gh_list_milestones():
        if m.get("title") == title:
            return m.get("number")
    r = gh_api("POST","milestones",{"title":title,"description":f"[MaxOS AI] {title}"})
    return r.get("number") if r else None

def gh_list_releases(n=10):
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

def git_cmd(args, cwd=None):
    r = subprocess.run(["git"]+args, cwd=cwd or REPO_PATH,
                       capture_output=True, text=True, timeout=60)
    return r.returncode==0, r.stdout, r.stderr

def get_sha():
    _, sha, _ = git_cmd(["rev-parse","HEAD"])
    return sha.strip()[:40]

def git_push(task_name, files, description, model):
    if not files: return True, None, None
    dirs   = set(f.split("/")[0] for f in files if "/" in f)
    pmap   = {"kernel":"kernel","drivers":"driver","boot":"boot",
               "ui":"ui","apps":"feat(apps)"}
    prefix = next((pmap[d] for d in pmap if d in dirs), "feat")
    fshort = ", ".join(os.path.basename(f) for f in files[:3])
    if len(files) > 3: fshort += f" +{len(files)-3}"
    short  = f"{prefix}: {task_name[:45]} [{fshort}]"
    body   = (f"\n\nFiles: {', '.join(files)}\nModel: {model}\n"
              f"Time: {datetime.utcnow().isoformat()}Z\nArch: x86-32 bare metal")
    git_cmd(["add","-A"])
    ok, out, err = git_cmd(["commit","-m",short+body])
    if not ok:
        if "nothing to commit" in (out+err):
            log("Rien à committer","GIT"); return True, None, None
        log(f"Commit KO: {err[:200]}","ERROR"); return False, None, None
    _, sha, _ = git_cmd(["rev-parse","HEAD"])
    sha        = sha.strip()[:7]
    ok2, _, e2 = git_cmd(["push"])
    if not ok2:
        git_cmd(["pull","--rebase"])
        ok2, _, e2 = git_cmd(["push"])
        if not ok2:
            log(f"Push KO: {e2[:200]}","ERROR"); return False, None, None
    log(f"Push OK: {sha}","GIT")
    return True, sha, short

BUILD_ERR_RE = re.compile(
    r"error:|fatal error:|fatal:|undefined reference|cannot find|no such file"
    r"|\*\*\* \[|Error \d+$|FAILED$|nasm:.*error|ld:.*error"
    r"|collect2: error|linker command failed|multiple definition|duplicate symbol",
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
    t0 = time.time()
    r  = subprocess.run(["make"], cwd=REPO_PATH,
                        capture_output=True, text=True, timeout=120)
    elapsed  = round(time.time()-t0, 1)
    ok       = r.returncode == 0
    log_text = r.stdout + r.stderr
    errs     = parse_build_errors(log_text)
    log(f"Build {'OK' if ok else 'ÉCHEC'} en {elapsed}s ({len(errs)} err)","BUILD")
    for e in errs[:3]: log(f"  >> {e[:100]}","BUILD")
    disc_build(ok, errs, elapsed)
    return ok, log_text, errs

SKIP_DIRS  = {".git","build","__pycache__",".github","ai_dev"}
SKIP_FILES = {"screen.h.save"}
SRC_EXTS   = {".c",".h",".asm",".ld"}

ALL_FILES = [
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

OS_MISSION = """MISSION: OS bare metal x86 complet.
OBJECTIF: IDT+PIC → Timer PIT → Mémoire bitmap → VGA 320x200 → Terminal 20cmds → FAT12 → GUI"""

RULES = """RÈGLES BARE METAL x86 ABSOLUES:
INTERDIT: #include<stddef.h|string.h|stdlib.h|stdio.h|stdint.h|stdbool.h>
INTERDIT: size_t NULL bool true false uint32_t uint8_t malloc memset strlen printf
REMPLACE: size_t→unsigned int | NULL→0 | bool→int | true→1 | false→0
          uint32_t→unsigned int | uint8_t→unsigned char
GCC: -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie
ASM: nasm -f elf (.o) | nasm -f bin (boot.bin)
LD: ld -m elf_i386 -T linker.ld --oformat binary
ZERO commentaire dans le code (gaspille les tokens)
kernel_entry.asm: _stack_top DOIT être un label global défini AVANT kernel_main
Nouveaux .c OBLIGATOIRES dans Makefile OBJS"""

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
    SOURCE_CACHE["hash"] = cur_hash
    SOURCE_CACHE["data"] = sources
    return sources

def build_context(sources, max_chars=38000):
    ctx  = "=== CODE SOURCE MAXOS ===\n\nFICHIERS:\n"
    for f,c in sources.items():
        ctx += f"  {'[OK]' if c else '[--]'} {f}\n"
    ctx  += "\n"
    used  = len(ctx)
    prio  = ["kernel/kernel.c","kernel/kernel_entry.asm","Makefile","linker.ld",
             "drivers/screen.h","drivers/keyboard.h","ui/ui.h"]
    done  = set()
    for f in prio:
        c = sources.get(f,"")
        if not c: continue
        block = f"{'='*48}\nFICHIER: {f}\n{'='*48}\n{c}\n\n"
        if used+len(block) > max_chars: continue
        ctx += block; used += len(block); done.add(f)
    for f,c in sources.items():
        if f in done or not c: continue
        block = f"{'='*48}\nFICHIER: {f}\n{'='*48}\n{c}\n\n"
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
    forbidden_inc = ["stddef.h","string.h","stdlib.h","stdio.h","stdint.h","stdbool.h"]
    forbidden_sym = ["size_t","NULL","bool","true","false","uint32_t","uint8_t",
                     "int32_t","malloc","free","memset","memcpy","strlen","printf","sprintf"]
    violations = []
    c_files = asm_files = total_lines = 0
    for fname, content in sources.items():
        if not content: continue
        if fname.endswith((".c",".h")):
            c_files += 1
            lines    = content.split("\n")
            total_lines += len(lines)
            for i, line in enumerate(lines, 1):
                s = line.strip()
                if s.startswith(("//","/*")): continue
                for inc in forbidden_inc:
                    if f"#include <{inc}>" in line or f'#include "{inc}"' in line:
                        violations.append(f"{fname}:{i} include:{inc}")
                for sym in forbidden_sym:
                    if re.search(r'\b'+re.escape(sym)+r'\b', line):
                        violations.append(f"{fname}:{i} sym:{sym}"); break
        elif fname.endswith(".asm"):
            asm_files   += 1
            total_lines += content.count("\n")
    score = max(0, 100-len(violations)*5)
    return {"score":score,"violations":violations[:20],
            "c_files":c_files,"asm_files":asm_files,"total_lines":total_lines}

def parse_files_from_resp(response):
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
    if not files and not to_del and response:
        log(f"Parse: rien trouvé. {response[:150]}","WARN")
    return files, to_del

def write_files(files):
    written = []
    for path, content in files.items():
        if path.startswith("/") or ".." in path: continue
        full = os.path.join(REPO_PATH, path)
        os.makedirs(os.path.dirname(full) or REPO_PATH, exist_ok=True)
        with open(full,"w",encoding="utf-8",newline="\n") as f:
            f.write(content)
        written.append(path)
        log(f"Écrit: {path}")
    SOURCE_CACHE["hash"] = None
    return written

def delete_files(paths):
    deleted = []
    for path in paths:
        if path.startswith("/") or ".." in path: continue
        full = os.path.join(REPO_PATH, path)
        if os.path.exists(full):
            os.remove(full); deleted.append(path)
            log(f"Supprimé: {path}")
    SOURCE_CACHE["hash"] = None
    return deleted

def backup_files(paths):
    bak = {}
    for p in paths:
        full = os.path.join(REPO_PATH, p)
        if os.path.exists(full):
            with open(full,"r",encoding="utf-8",errors="ignore") as f:
                bak[p] = f.read()
    return bak

def restore_files(bak):
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
        "fonctionnalites_presentes": ["Boot x86","VGA texte","Clavier PS/2","4 apps"],
        "fonctionnalites_manquantes_critiques": ["IDT","Timer PIT","Mémoire","VGA graphique","FAT12"],
        "prochaine_milestone": "Kernel stable IDT+Timer",
        "plan_ameliorations": [
            {
                "nom":"IDT 256 entrées + PIC 8259 + handlers",
                "priorite":"CRITIQUE","categorie":"kernel",
                "fichiers_a_modifier":["kernel/kernel.c","kernel/kernel_entry.asm","Makefile"],
                "fichiers_a_creer":["kernel/idt.h","kernel/idt.c"],
                "fichiers_a_supprimer":[],
                "description":(
                    "kernel_entry.asm: multiboot header, global _stack_top label, "
                    "pile 16KB resb, call kernel_main. "
                    "idt.h: struct IDTEntry 8 bytes packed, struct IDTPtr, prototypes. "
                    "idt.c: idt_set_gate, idt_init 256 gates, PIC 8259 remap IRQ0-7→0x20 "
                    "IRQ8-15→0x28, 48 stubs ASM extern, isr_handler irq_handler avec EOI, "
                    "panic() affiche rouge. kernel.c appelle idt_init puis sti."
                ),
                "impact_attendu":"OS stable sans triple fault",
                "complexite":"HAUTE"
            },
            {
                "nom":"Timer PIT 8253 100Hz + uptime + sleep_ms",
                "priorite":"CRITIQUE","categorie":"kernel",
                "fichiers_a_modifier":["kernel/kernel.c","Makefile"],
                "fichiers_a_creer":["kernel/timer.h","kernel/timer.c"],
                "fichiers_a_supprimer":[],
                "description":(
                    "timer.h: timer_init() timer_ticks() sleep_ms(unsigned int ms) uptime_str(char*). "
                    "timer.c: PIT canal 0 diviseur 11931=100Hz outb 0x43 outb 0x40, "
                    "volatile unsigned int ticks, IRQ0 handler incrémente ticks, "
                    "uptime HH:MM:SS depuis ticks."
                ),
                "impact_attendu":"Horloge + sleep fonctionnels",
                "complexite":"MOYENNE"
            },
            {
                "nom":"Terminal 20 commandes + historique flèches",
                "priorite":"HAUTE","categorie":"app",
                "fichiers_a_modifier":["apps/terminal.h","apps/terminal.c"],
                "fichiers_a_creer":[],
                "fichiers_a_supprimer":[],
                "description":(
                    "20 commandes: help ver mem uptime cls echo date reboot halt "
                    "color beep calc about credits clear ps sysinfo license snake pong time. "
                    "Historique 20 entrées flèche haut/bas. Parser arguments. ZERO stdlib."
                ),
                "impact_attendu":"Terminal complet type cmd.exe",
                "complexite":"MOYENNE"
            },
            {
                "nom":"Allocateur mémoire bitmap 4KB pages",
                "priorite":"HAUTE","categorie":"kernel",
                "fichiers_a_modifier":["kernel/kernel.c","Makefile"],
                "fichiers_a_creer":["kernel/memory.h","kernel/memory.c"],
                "fichiers_a_supprimer":[],
                "description":(
                    "memory.h: mem_init(unsigned int start, unsigned int end) "
                    "mem_alloc()→unsigned int mem_free(unsigned int addr) mem_used() mem_total(). "
                    "memory.c: bitmap[256] unsigned int pour 32MB/4KB=8192 bits, "
                    "ZERO NULL→0 ZERO stdlib."
                ),
                "impact_attendu":"Allocation mémoire sans malloc",
                "complexite":"HAUTE"
            },
            {
                "nom":"VGA mode 13h 320x200 + desktop graphique",
                "priorite":"NORMALE","categorie":"driver",
                "fichiers_a_modifier":["drivers/screen.h","drivers/screen.c","kernel/kernel.c","Makefile"],
                "fichiers_a_creer":["drivers/vga.h","drivers/vga.c"],
                "fichiers_a_supprimer":[],
                "description":(
                    "vga.h: v_init() v_pixel(int x,int y,unsigned char c) "
                    "v_rect(int x,int y,int w,int h,unsigned char c) v_fill(unsigned char c) "
                    "v_line(int x1,int y1,int x2,int y2,unsigned char c). "
                    "vga.c: mode 13h via outb 0x3C8/0x3C9, framebuffer*(unsigned char*)0xA0000, "
                    "desktop background bleu taskbar grise bas 10px."
                ),
                "impact_attendu":"Interface graphique 256 couleurs",
                "complexite":"HAUTE"
            }
        ]
    }

def phase_analyse(context, stats):
    log("\n=== PHASE 1: ANALYSE ===")
    disc_force("🔍 Analyse du projet",
               f"`{stats['files']}` fichiers | `{stats['lines']}` lignes",
               0x5865F2)
    prompt = (
        f"Expert OS bare metal x86.\n{RULES}\n{OS_MISSION}\n\n"
        f"{context}\n\n"
        f"STATS: {stats['files']} fichiers, {stats['lines']} lignes\n\n"
        "Retourne UNIQUEMENT ce JSON:\n"
        '{"score_actuel":30,"niveau_os":"Prototype bare metal",'
        '"fonctionnalites_presentes":["Boot x86"],'
        '"fonctionnalites_manquantes_critiques":["IDT"],'
        '"plan_ameliorations":[{"nom":"IDT","priorite":"CRITIQUE","categorie":"kernel",'
        '"fichiers_a_modifier":["kernel/kernel.c"],"fichiers_a_creer":["kernel/idt.h"],'
        '"fichiers_a_supprimer":[],"description":"specs techniques","impact_attendu":"résultat","complexite":"HAUTE"}],'
        '"prochaine_milestone":"Kernel stable"}'
    )
    resp = ai_call(prompt, max_tokens=3000, timeout=60, tag="analyse")
    if not resp:
        log("Analyse IA KO → plan défaut","WARN")
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
                n_tasks = len(result.get("plan_ameliorations",[]))
                log(f"Analyse OK: score={result.get('score_actuel','?')} | {n_tasks} tâches","OK")
                return result
            except json.JSONDecodeError as e:
                log(f"JSON err: {e}","WARN")
                clean = clean[i+1:]
    log("JSON impossible → plan défaut","WARN")
    return default_plan()

def build_impl_prompt(task, ctx):
    nom   = task.get("nom","?")
    cat   = task.get("categorie","general")
    cx    = task.get("complexite","MOYENNE")
    desc  = task.get("description","")
    f_mod = task.get("fichiers_a_modifier",[])
    f_new = task.get("fichiers_a_creer",[])
    f_del = task.get("fichiers_a_supprimer",[])
    return (
        f"{RULES}\n\n"
        f"TÂCHE: {nom}\n"
        f"CAT: {cat} | CX: {cx}\n"
        f"MODIFIER: {f_mod}\n"
        f"CRÉER: {f_new}\n"
        f"SUPPRIMER: {f_del}\n"
        f"SPECS: {desc}\n\n"
        f"CODE EXISTANT:\n{ctx}\n\n"
        "RÈGLES DE SORTIE ABSOLUES:\n"
        "1. Code 100% complet, ZÉRO commentaire, ZÉRO '...', ZÉRO placeholder\n"
        "2. ZÉRO include stdlib, ZÉRO NULL→0, ZÉRO bool→int, ZÉRO uint32_t→unsigned int\n"
        "3. kernel_entry.asm: label global _stack_top OBLIGATOIRE avant kernel_main\n"
        "4. Chaque nouveau .c dans Makefile OBJS\n"
        "5. Supprimer: === DELETE: chemin ===\n\n"
        "FORMAT STRICT OBLIGATOIRE:\n"
        "=== FILE: chemin/fichier.ext ===\n"
        "[code complet]\n"
        "=== END FILE ===\n\n"
        "GÉNÈRE MAINTENANT TOUS LES FICHIERS:"
    )

def build_task_context(task, all_sources):
    f_mod  = task.get("fichiers_a_modifier",[])
    f_new  = task.get("fichiers_a_creer",[])
    needed = set(f_mod+f_new)
    for f in list(needed):
        partner = f.replace(".c",".h") if f.endswith(".c") else f.replace(".h",".c")
        if partner in all_sources: needed.add(partner)
    for ess in ["kernel/kernel.c","kernel/kernel_entry.asm","Makefile","linker.ld","drivers/screen.h"]:
        needed.add(ess)
    ctx = ""
    used = 0
    for f in sorted(needed):
        c     = all_sources.get(f,"")
        block = f"--- {f} ---\n{c if c else '[À CRÉER]'}\n\n"
        if used+len(block) > 18000: ctx += f"[{f} tronqué]\n"; continue
        ctx += block; used += len(block)
    return ctx

def auto_fix(build_log_text, errs, gen_files, bak, model, max_attempts=3):
    log(f"Auto-fix: {len(errs)} erreur(s)","BUILD")
    cur_log  = build_log_text
    cur_errs = errs
    for attempt in range(1, max_attempts+1):
        log(f"Fix tentative {attempt}/{max_attempts}","BUILD")
        disc_log(f"🔧 Fix {attempt}/{max_attempts}",
                 f"`{len(cur_errs)}` erreur(s) à corriger",0x00AAFF)
        curr = {}
        for p in gen_files:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp):
                with open(fp,"r") as f: curr[p] = f.read()[:8000]
        ctx     = "".join(f"--- {p} ---\n{c}\n\n" for p,c in curr.items())
        err_str = "\n".join(cur_errs[:10])
        prompt  = (
            f"{RULES}\n\n"
            f"ERREURS:\n```\n{err_str}\n```\n\n"
            f"LOG FIN:\n```\n{cur_log[-1200:]}\n```\n\n"
            f"FICHIERS ACTUELS:\n{ctx}\n\n"
            "CORRIGE TOUT. ZÉRO commentaire. ZÉRO stdlib. "
            "_stack_top = label global dans kernel_entry.asm.\n"
            "FORMAT:\n=== FILE: fichier ===\n[code]\n=== END FILE ==="
        )
        resp = ai_call(prompt, max_tokens=24576, timeout=90, tag=f"fix/{attempt}")
        if not resp: continue
        files, _ = parse_files_from_resp(resp)
        if not files: log("Fix: rien parsé","WARN"); continue
        write_files(files)
        ok, cur_log, cur_errs = make_build()
        if ok:
            git_push("fix: corrections compilation", list(files.keys()),
                     f"Auto-fix: {len(errs)} erreurs→0", model)
            disc_force("🔧 Auto-fix ✅",
                       f"{len(errs)} erreur(s) corrigée(s) en {attempt} tentative(s).",0x00AAFF)
            return True, {"attempts": attempt}
        log(f"Fix {attempt}: {len(cur_errs)} erreur(s) restante(s)","WARN")
        time.sleep(6)
    restore_files(bak)
    return False, {"attempts": max_attempts}

def implement_task(task, all_sources, i, total):
    nom   = task.get("nom","?")
    cat   = task.get("categorie","general")
    cx    = task.get("complexite","MOYENNE")
    desc  = task.get("description","")
    f_mod = task.get("fichiers_a_modifier",[])
    f_new = task.get("fichiers_a_creer",[])
    model = next(
        (p["model"] for p in PROVIDERS
         if not p["forbidden"] and time.time() >= p["cooldown"]),
        "?"
    )
    log(f"\n{'='*55}")
    log(f"[{i}/{total}] {nom}")
    log(f"  Cat={cat} Cx={cx}")
    log(f"{'='*55}")
    disc_task_start(i, total, nom, task.get("priorite","?"), cat, desc)

    t_start = time.time()
    targets = list(set(f_mod+f_new))
    ctx     = build_task_context(task, all_sources)
    tok_map = {"HAUTE":32768,"MOYENNE":20480,"BASSE":12288}
    max_tok = tok_map.get(cx, 20480)
    prompt  = build_impl_prompt(task, ctx)

    disc_log(f"⏳ Génération [{nom[:35]}]",
             f"Prompt: `{len(prompt):,}` chars | max_tokens: `{max_tok}`\n"
             f"Cibles: {', '.join(f'`{f}`' for f in targets[:4])}",
             0xFFA500)

    resp    = ai_call(prompt, max_tokens=max_tok, timeout=160, tag=f"impl/{nom[:18]}")
    elapsed = round(time.time()-t_start, 1)

    if not resp:
        disc_task_fail(i, total, nom, "ai_fail", [], elapsed)
        return False, [], [], {"nom":nom,"elapsed":elapsed,"result":"ai_fail","errors":[]}

    log(f"Réponse: {len(resp)} chars en {elapsed}s")
    files, to_del = parse_files_from_resp(resp)

    if not files and not to_del:
        disc_task_fail(i, total, nom, "parse_empty", [], elapsed)
        return False, [], [], {"nom":nom,"elapsed":elapsed,"result":"parse_empty","errors":[]}

    disc_log(f"📁 {len(files)} fichier(s) parsé(s)",
             "\n".join(f"`{f}` {len(c):,}ch" for f,c in list(files.items())[:8]),
             0x00AAFF)

    bak     = backup_files(list(files.keys()))
    written = write_files(files)
    deleted = delete_files(to_del)

    if not written and not deleted:
        disc_task_fail(i, total, nom, "no_files", [], elapsed)
        return False, [], [], {"nom":nom,"elapsed":elapsed,"result":"no_files","errors":[]}

    ok, build_log_text, errs = make_build()

    if ok:
        pushed, sha, _ = git_push(nom, written+deleted, desc, model)
        if pushed:
            metrics = {"nom":nom,"elapsed":round(time.time()-t_start,1),
                       "result":"success","sha":sha,"files":written+deleted,
                       "model":model,"fix_count":0}
            disc_task_ok(i, total, nom, sha or "?", written, deleted,
                         metrics["elapsed"], 0)
            return True, written, deleted, metrics
        restore_files(bak)
        disc_task_fail(i, total, nom, "push_fail", [], elapsed)
        return False, [], [], {"nom":nom,"elapsed":elapsed,"result":"push_fail","errors":[]}

    fixed, fix_m = auto_fix(build_log_text, errs, list(files.keys()), bak, model)
    if fixed:
        metrics = {"nom":nom,"elapsed":round(time.time()-t_start,1),
                   "result":"success_after_fix","files":written+deleted,
                   "model":model,"fix_count":fix_m.get("attempts",0),"sha":"fixed"}
        disc_task_ok(i, total, nom, "fixed", written, deleted,
                     metrics["elapsed"], metrics["fix_count"])
        return True, written, deleted, metrics

    restore_files(bak)
    for p in written:
        if p not in bak:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp): os.remove(fp)
    SOURCE_CACHE["hash"] = None
    disc_task_fail(i, total, nom, "build_fail", errs, round(time.time()-t_start,1))
    return False, [], [], {"nom":nom,"elapsed":round(time.time()-t_start,1),
                           "result":"build_fail","errors":errs[:5]}

def handle_issues():
    issues = gh_open_issues()
    if not issues: log("Issues: aucune"); return
    log(f"Issues: {len(issues)} à traiter")
    bot_logins = {"MaxOS-AI-Bot","github-actions[bot]"}
    for issue in issues[:8]:
        num    = issue.get("number")
        title  = issue.get("title","")
        author = issue.get("user",{}).get("login","")
        if author in bot_logins: continue
        timeline = gh_issue_timeline(num)
        if any(e.get("actor",{}).get("login","") in bot_logins or
               e.get("user",{}).get("login","") in bot_logins
               for e in (timeline or [])): continue
        log(f"Issue #{num}: {title[:50]}")
        prompt = (
            f"Bot issues OS bare metal x86 MaxOS.\n"
            f"ISSUE #{num}: {title}\nAuteur: {author}\n"
            f"Corps: {(issue.get('body','') or '')[:600]}\n\n"
            "JSON UNIQUEMENT:\n"
            '{"type":"bug|enhancement|question|invalid",'
            '"labels":["bug","kernel"],"action":"respond|close|label_only",'
            '"close_reason":"completed|not_planned",'
            '"response":"réponse courte utile en français"}'
        )
        resp = ai_call(prompt, max_tokens=800, timeout=30, tag=f"issue/{num}")
        if not resp: continue
        clean = resp.strip()
        if clean.startswith("```"):
            lines = clean.split("\n")[1:]
            if lines and lines[-1].strip()=="```": lines=lines[:-1]
            clean = "\n".join(lines).strip()
        try:
            i = clean.find("{"); j = clean.rfind("}")+1
            if i >= 0 and j > i:
                a       = json.loads(clean[i:j])
                action  = a.get("action","label_only")
                labels  = [l for l in a.get("labels",[]) if l in STANDARD_LABELS]
                response= a.get("response","")
                itype   = a.get("type","?")
                if labels: gh_add_labels(num, labels)
                if response and action in ("respond","close","close_not_planned"):
                    icon = {"bug":"🐛","enhancement":"✨","question":"❓"}.get(itype,"💬")
                    gh_comment(num,
                        f"{icon} **MaxOS AI** — Réponse automatique\n\n{response}\n\n"
                        f"---\n*MaxOS AI v{VERSION} | {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC*")
                if action == "close":
                    gh_close_issue(num,"completed")
                elif action == "close_not_planned":
                    gh_close_issue(num,"not_planned")
                disc_log(f"🎫 Issue #{num}",
                         f"**{title[:45]}** | `{itype}` | `{action}`",0x00FF88)
                log(f"Issue #{num} → {action} ({itype})","OK")
        except Exception as ex:
            log(f"Issue #{num} err: {ex}","WARN")
        time.sleep(1)

def handle_stale(days_stale=21, days_close=7):
    issues = gh_open_issues()
    now    = time.time()
    for issue in issues:
        num       = issue.get("number")
        updated   = issue.get("updated_at","")
        labels    = [l.get("name","") for l in issue.get("labels",[])]
        is_stale  = "stale" in labels
        try: updated_ts = datetime.strptime(updated,"%Y-%m-%dT%H:%M:%SZ").timestamp()
        except: continue
        age = now - updated_ts
        if age >= (days_stale+days_close)*86400 and is_stale:
            gh_comment(num,"🤖 **MaxOS AI**: Issue fermée (inactive). Rouvrez si besoin.")
            gh_close_issue(num,"not_planned")
        elif age >= days_stale*86400 and not is_stale:
            gh_add_labels(num,["stale"])
            gh_comment(num,
                f"⏰ **MaxOS AI**: Inactive depuis {int(age/86400)} jours. "
                f"Fermeture dans **{days_close} jours** sans réponse.")

def handle_prs():
    prs = gh_open_prs()
    if not prs: log("PRs: aucune"); return
    log(f"PRs: {len(prs)} à traiter")
    bot_logins = {"MaxOS-AI-Bot","github-actions[bot]"}
    for pr in prs[:4]:
        num    = pr.get("number")
        title  = pr.get("title","")
        author = pr.get("user",{}).get("login","")
        if author in bot_logins: continue
        if any(r.get("user",{}).get("login","") in bot_logins
               for r in (gh_pr_reviews(num) or [])): continue
        log(f"PR #{num}: {title[:50]}")
        files_data = gh_pr_files(num)
        file_list  = "\n".join(
            f"- {f.get('filename','?')} (+{f.get('additions',0)}-{f.get('deletions',0)})"
            for f in files_data[:12]
        )
        patches = ""
        for f in [x for x in files_data
                  if any(x.get("filename","").endswith(e) for e in [".c",".h",".asm"])][:4]:
            patches += f"\n--- {f.get('filename','?')} ---\n{f.get('patch','')[:800]}\n"
        prompt = (
            f"Expert OS bare metal x86. Code review PR.\n{RULES}\n\n"
            f"PR #{num}: {title}\nAuteur: {author}\n"
            f"Fichiers:\n{file_list}\nChangements:\n{patches}\n\n"
            "JSON UNIQUEMENT:\n"
            '{"decision":"APPROVE|REQUEST_CHANGES|COMMENT",'
            '"summary":"2 phrases","problems":["p1"],"positives":["p1"],'
            '"merge_safe":false,"violations":["v1"]}'
        )
        resp = ai_call(prompt, max_tokens=1500, timeout=40, tag=f"pr/{num}")
        if not resp: continue
        clean = resp.strip()
        if clean.startswith("```"):
            lines = clean.split("\n")[1:]
            if lines and lines[-1].strip()=="```": lines=lines[:-1]
            clean = "\n".join(lines).strip()
        try:
            i = clean.find("{"); j = clean.rfind("}")+1
            if i >= 0 and j > i:
                a          = json.loads(clean[i:j])
                decision   = a.get("decision","COMMENT")
                merge_safe = a.get("merge_safe",False)
                summary    = a.get("summary","")
                problems   = a.get("problems",[])
                positives  = a.get("positives",[])
                violations = a.get("violations",[])
                icon       = {"APPROVE":"✅","REQUEST_CHANGES":"🔴","COMMENT":"💬"}.get(decision,"💬")
                body       = (
                    f"## {icon} Code Review MaxOS AI — PR #{num}\n\n"
                    f"> **{decision}** | Safe: {'🟢' if merge_safe else '🔴'}\n\n{summary}\n\n"
                )
                if problems:   body += "### ❌ Problèmes\n" + "\n".join(f"- {p}" for p in problems)+"\n\n"
                if positives:  body += "### ✅ Positifs\n"  + "\n".join(f"- {p}" for p in positives)+"\n\n"
                if violations: body += "### ⚠️ Violations\n"+ "\n".join(f"- `{v}`" for v in violations)+"\n\n"
                body += f"---\n*MaxOS AI v{VERSION}*"
                event = "APPROVE" if decision=="APPROVE" and merge_safe else \
                        "REQUEST_CHANGES" if decision=="REQUEST_CHANGES" else "COMMENT"
                gh_post_review(num, body, event)
                labels_to_add = (["ai-approved","ai-reviewed"] if decision=="APPROVE" else
                                 ["ai-rejected","ai-reviewed","needs-fix"] if decision=="REQUEST_CHANGES" else
                                 ["ai-reviewed"])
                gh_add_labels(num, labels_to_add)
                disc_log(f"📋 PR #{num} {decision}",
                         f"**{title[:45]}** | Safe: {'✅' if merge_safe else '❌'}",
                         0x00AAFF if decision=="APPROVE" else 0xFF4444 if decision=="REQUEST_CHANGES" else 0xFFA500)
                log(f"PR #{num} → {decision}","OK")
        except Exception as ex:
            log(f"PR #{num} err: {ex}","WARN")
        time.sleep(1.5)

def generate_changelog(last_tag, tasks_done):
    compare = gh_compare(last_tag,"HEAD")
    commits = compare.get("commits",[])
    groups  = {"kernel":[],"driver":[],"feat":[],"fix":[],"other":[]}
    for commit in commits[:25]:
        msg = commit.get("commit",{}).get("message","").split("\n")[0]
        sha = commit.get("sha","")[:7]
        if not msg: continue
        entry = f"- `{sha}` {msg[:75]}"
        if   msg.startswith("kernel:"): groups["kernel"].append(entry)
        elif msg.startswith("driver:"): groups["driver"].append(entry)
        elif msg.startswith("feat"):    groups["feat"].append(entry)
        elif msg.startswith("fix:"):    groups["fix"].append(entry)
        else:                           groups["other"].append(entry)
    labels = {"kernel":"🔧 Kernel","driver":"💾 Drivers","feat":"✨ Features",
              "fix":"🐛 Fixes","other":"📝 Autres"}
    out = ""
    for key, entries in groups.items():
        if entries: out += f"### {labels[key]}\n" + "\n".join(entries) + "\n\n"
    return out or "\n".join(f"- {t.get('nom','?')[:60]}" for t in tasks_done)

def create_release(tasks_done, tasks_failed, analyse, stats):
    releases = gh_list_releases(5)
    last_tag = "v0.0.0"
    for r in releases:
        tag = r.get("tag_name","")
        if re.match(r"v\d+\.\d+\.\d+",tag): last_tag=tag; break
    try:
        parts = last_tag.lstrip("v").split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    except: major, minor, patch = 0,0,0
    score = analyse.get("score_actuel",30)
    if score >= 70: minor += 1; patch = 0
    else: patch += 1
    new_tag   = f"v{major}.{minor}.{patch}"
    niveau    = analyse.get("niveau_os","?")
    ms        = analyse.get("prochaine_milestone","?")
    feats     = analyse.get("fonctionnalites_presentes",[])
    feat_txt  = "\n".join(f"- ✅ {f}" for f in feats[:8]) or "- (Aucune)"
    changes_txt = "".join(
        f"- ✅ {t.get('nom','?')[:55]} [`{t.get('sha','?')}`] ({t.get('model','?')})"
        + (f" fix×{t.get('fix_count',0)}" if t.get("fix_count",0) else "") + "\n"
        for t in tasks_done
    ) or "- Maintenance\n"
    failed_txt = (
        "\n## ⏭️ Reporté\n\n" +
        "\n".join(f"- ❌ {n}" for n in tasks_failed) + "\n"
    ) if tasks_failed else ""
    total_elapsed = round(time.time()-START_TIME, 0)
    total_tokens  = sum(p["tokens"] for p in PROVIDERS)
    total_calls   = sum(p["calls"]  for p in PROVIDERS)
    changelog     = generate_changelog(last_tag, tasks_done)
    now           = datetime.utcnow()
    providers_used = ", ".join(sorted(set(
        p["type"] for p in PROVIDERS if p["calls"] > 0
    ))) or "gemini"
    body = (
        f"# MaxOS {new_tag}\n\n"
        f"> 🤖 MaxOS AI Developer v{VERSION} | Multi-provider\n\n"
        f"| | |\n|---|---|\n"
        f"| Score | **{score}/100** |\n"
        f"| Niveau | {niveau} |\n"
        f"| Fichiers | {stats.get('files',0)} |\n"
        f"| Lignes | {stats.get('lines',0)} |\n"
        f"| Milestone | {ms} |\n\n"
        f"## ✅ Changements\n\n{changes_txt}"
        f"{failed_txt}"
        f"\n## 🧩 Fonctionnalités\n\n{feat_txt}\n\n"
        f"{changelog}\n"
        f"---\n\n## 🚀 Tester\n\n"
        f"```bash\nsudo apt install qemu-system-x86\n"
        f"qemu-system-i386 -drive format=raw,file=os.img,if=floppy "
        f"-boot a -vga std -k fr -m 32 -no-reboot\n```\n\n"
        f"## ⚙️ Technique\n\n"
        f"| | |\n|---|---|\n"
        f"| Arch | x86 32-bit Protected Mode |\n"
        f"| CC | GCC -m32 -ffreestanding -nostdlib |\n"
        f"| IA | {providers_used} |\n"
        f"| Appels | {total_calls} |\n"
        f"| ~Tokens | {total_tokens} |\n"
        f"| Durée | {int(total_elapsed)}s |\n\n"
        f"---\n*MaxOS AI v{VERSION} | {now.strftime('%Y-%m-%d %H:%M')} UTC*\n"
    )
    url = gh_create_release(new_tag,
                            f"MaxOS {new_tag} | {niveau} | {now.strftime('%Y-%m-%d')}",
                            body, pre=(score<50))
    if url:
        disc_force("🚀 Release créée", f"**{new_tag}** | {score}/100 | {niveau}", 0x00FF88,
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
    total_elapsed = round(time.time()-START_TIME, 0)
    total_tokens  = sum(p["tokens"] for p in PROVIDERS)
    total_calls   = sum(p["calls"]  for p in PROVIDERS)
    sources       = read_all()
    quality       = analyze_quality(sources)
    done_str = "\n".join(
        f"✅ {t.get('nom','?')[:38]} ({t.get('elapsed',0):.0f}s)" for t in tasks_done
    ) or "Aucune"
    fail_str = "\n".join(f"❌ {n[:38]}" for n in tasks_failed) or "Aucune"
    disc_force(
        f"🏁 Cycle terminé — {success}/{total} réussies",
        f"```\n{pbar(pct)}\n```",
        color,
        [{"name":"✅ Succès","value":str(success),"inline":True},
         {"name":"❌ Échecs","value":str(total-success),"inline":True},
         {"name":"📈 Taux","value":f"{pct}%","inline":True},
         {"name":"⏱️ Durée","value":f"{int(total_elapsed)}s","inline":True},
         {"name":"🔑 Appels","value":str(total_calls),"inline":True},
         {"name":"💬 ~Tokens","value":str(total_tokens),"inline":True},
         {"name":"📊 Qualité","value":f"{quality['score']}/100","inline":True},
         {"name":"📁 Fichiers","value":str(stats.get("files",0)),"inline":True},
         {"name":"📝 Lignes","value":str(stats.get("lines",0)),"inline":True},
         {"name":"📊 Score OS","value":f"{score}/100 — {niveau}","inline":False},
         {"name":"✅ Réussies","value":done_str[:800],"inline":False},
         {"name":"❌ Échouées","value":fail_str[:400],"inline":False},
         {"name":"🔑 Providers","value":providers_summary()[:800],"inline":False}]
    )
    if quality["violations"]:
        viols = "\n".join(f"• `{v}`" for v in quality["violations"][:10])
        disc_force("⚠️ Violations bare metal",f"```\n{viols}\n```",0xFF6600)

def cleanup():
    build_dir = os.path.join(REPO_PATH,"build")
    if not os.path.exists(build_dir): return
    cleaned = 0
    for fname in os.listdir(build_dir):
        if fname.endswith((".o",".img.old")):
            try: os.remove(os.path.join(build_dir,fname)); cleaned += 1
            except: pass
    if cleaned: log(f"Cleanup: {cleaned} fichier(s)")

def main():
    print("="*58)
    print(f"  MaxOS AI Developer v{VERSION}")
    print(f"  {len(PROVIDERS)} providers | Multi-API | Anti-429")
    print("="*58)
    for p in PROVIDERS[:8]:
        print(f"  {p['type']:10} | {mask(p['key'])} | {p['model'][:25]}")
    if len(PROVIDERS) > 8:
        print(f"  ... +{len(PROVIDERS)-8} providers")
    print("="*58)

    if not PROVIDERS:
        print("FATAL: Aucun provider configuré")
        sys.exit(1)

    disc_force(
        f"🤖 MaxOS AI v{VERSION} démarré",
        f"`{len(PROVIDERS)}` providers configurés",
        0x5865F2,
        [{"name":"Providers","value":providers_summary()[:900],"inline":False},
         {"name":"Repo","value":f"{REPO_OWNER}/{REPO_NAME}","inline":True},
         {"name":"Mode","value":"Multi-provider anti-429","inline":True}]
    )

    cleanup()

    log("Setup labels GitHub...")
    created = gh_ensure_labels(STANDARD_LABELS)
    if created: disc_log(f"🏷️ {created} label(s) créé(s)","",0x5865F2)

    log("Traitement des issues...")
    handle_issues()
    if not watchdog(): sys.exit(0)

    log("Stale bot...")
    handle_stale()

    log("Traitement des PRs...")
    handle_prs()
    if not watchdog(): sys.exit(0)

    sources = read_all(force=True)
    stats   = proj_stats(sources)
    quality = analyze_quality(sources)
    log(f"Sources: {stats['files']} fichiers, {stats['lines']} lignes")

    disc_force("📊 Sources analysées",
               f"`{stats['files']}` fichiers | `{stats['lines']}` lignes | `{stats['chars']}` chars",
               0x5865F2,
               [{"name":"Qualité","value":f"{quality['score']}/100 ({len(quality['violations'])} violations)","inline":True},
                {"name":".c files","value":str(quality.get("c_files",0)),"inline":True},
                {"name":".asm files","value":str(quality.get("asm_files",0)),"inline":True}])

    print("\n"+"="*58+"\n PHASE 1: Analyse\n"+"="*58)
    analyse = phase_analyse(build_context(sources), stats)

    score     = analyse.get("score_actuel",30)
    niveau    = analyse.get("niveau_os","?")
    plan      = analyse.get("plan_ameliorations",[])
    milestone = analyse.get("prochaine_milestone","?")
    features  = analyse.get("fonctionnalites_presentes",[])
    manques   = analyse.get("fonctionnalites_manquantes_critiques",[])

    order = {"CRITIQUE":0,"HAUTE":1,"NORMALE":2,"BASSE":3}
    plan  = sorted(plan, key=lambda t: order.get(t.get("priorite","NORMALE"),2))

    log(f"Score={score} | {niveau} | {len(plan)} tâches | {milestone}","OK")

    if milestone and milestone != "?":
        ms_num = gh_ensure_milestone(milestone)
        if ms_num: log(f"Milestone '{milestone}' = #{ms_num}")

    disc_force(
        f"📊 Score {score}/100 — {niveau}",
        f"```\n{pbar(score)}\n```",
        0x00AAFF if score>=60 else 0xFFA500 if score>=30 else 0xFF4444,
        [{"name":"✅ Présentes","value":"\n".join(f"+ {f}" for f in features[:5]) or "?","inline":True},
         {"name":"❌ Manquantes","value":"\n".join(f"- {f}" for f in manques[:5]) or "?","inline":True},
         {"name":"📋 Plan","value":"\n".join(
             f"[{i+1}] `{t.get('priorite','?')}` {t.get('nom','?')[:32]}"
             for i,t in enumerate(plan[:6])
         ),"inline":False},
         {"name":"🎯 Milestone","value":milestone[:80],"inline":True},
         {"name":"🔑 Providers","value":providers_summary()[:500],"inline":False}]
    )

    print("\n"+"="*58+"\n PHASE 2: Implémentation\n"+"="*58)

    total        = len(plan)
    success      = 0
    tasks_done   = []
    tasks_failed = []

    for i, task in enumerate(plan, 1):
        if not watchdog(): break
        disc_heartbeat(i, total,
                       f"Prochaine: **{task.get('nom','?')[:45]}**")
        sources_fresh = read_all()
        ok, written, deleted, metrics = implement_task(task, sources_fresh, i, total)
        TASK_METRICS.append(metrics)
        if ok:
            success += 1
            tasks_done.append(metrics)
        else:
            tasks_failed.append(task.get("nom","?"))
        if i < total:
            now    = time.time()
            n_ok   = sum(1 for p in PROVIDERS
                         if not p["forbidden"] and now >= p["cooldown"])
            pause  = 5 if n_ok >= 3 else 10 if n_ok >= 1 else 20
            log(f"Pause {pause}s ({n_ok} providers dispo)...")
            flush_disc(force=True)
            time.sleep(pause)

    if success > 0:
        sources_f = read_all(force=True)
        create_release(tasks_done, tasks_failed, analyse, proj_stats(sources_f))

    sources_f = read_all(force=True)
    final_report(success, total, tasks_done, tasks_failed, analyse, proj_stats(sources_f))
    flush_disc(force=True)

    print("\n"+"="*58)
    print(f"[FIN] {success}/{total} | Uptime: {uptime()} | RL: {GH_RATE['remaining']}")
    if tasks_done:
        print("✅ Succès:")
        for t in tasks_done:
            print(f"  - {t.get('nom','?')[:55]} ({t.get('elapsed',0):.0f}s)")
    if tasks_failed:
        print("❌ Échecs:")
        for n in tasks_failed:
            print(f"  - {n[:55]}")

if __name__ == "__main__":
    main()
