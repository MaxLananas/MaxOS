#!/usr/bin/env python3
import os, sys, json, time, subprocess, re, hashlib, traceback
import urllib.request, urllib.error
from datetime import datetime, timezone

VERSION    = "11.0"
DEBUG      = os.environ.get("MAXOS_DEBUG", "0") == "1"
START_TIME = time.time()

def load_keys():
    keys = []
    k = os.environ.get("GEMINI_API_KEY", "")
    if k: keys.append(k)
    for i in range(2, 10):
        k = os.environ.get(f"GEMINI_API_KEY_{i}", "")
        if k: keys.append(k)
    return keys

API_KEYS     = load_keys()
GH_TOKEN     = os.environ.get("GH_PAT","") or os.environ.get("GITHUB_TOKEN","")
DISCORD_WH   = os.environ.get("DISCORD_WEBHOOK","")
REPO_OWNER   = os.environ.get("REPO_OWNER","MaxLananas")
REPO_NAME    = os.environ.get("REPO_NAME","MaxOS")
REPO_PATH    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash-8b",
]

KEY_STATE = {
    "idx":       0,
    "cooldowns": {},
    "errors":    {},
    "usage":     {},
    "forbidden": {},
    "tokens":    {},
}
ACTIVE_MODELS  = {}
SOURCE_CACHE   = {"hash": None, "data": None}
GH_RATE        = {"remaining": 5000, "reset": 0}
TASK_METRICS   = []
MAX_RUNTIME    = 3200

def ts():
    return datetime.now(timezone.utc).strftime("%H:%M:%S")

def uptime():
    s = int(time.time() - START_TIME)
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def log(msg, level="INFO"):
    icons = {"INFO":"📋","WARN":"⚠️","ERROR":"❌","OK":"✅","BUILD":"🔨",
             "GEM":"🤖","GIT":"📦","DISC":"📢","NET":"🌐","TIME":"⏱️"}
    prefix = icons.get(level, "📋")
    print(f"[{ts()}] {prefix} {msg}", flush=True)

def mask(k):
    return k[:6] + "***" + k[-4:] if len(k) > 10 else "***"

def pbar(pct, w=24):
    f = int(w * pct / 100)
    return "█"*f + "░"*(w-f) + f" {pct}%"

def watchdog():
    if time.time() - START_TIME >= MAX_RUNTIME:
        log(f"Watchdog: limite {MAX_RUNTIME}s atteinte", "WARN")
        disc_send_simple("⏰ Watchdog déclenché", f"Arrêt après {uptime()}", 0xFFA500)
        return False
    return True

print("="*60)
print(f"  MaxOS AI Developer v{VERSION}")
print(f"  {len(API_KEYS)} clé(s) Gemini | Batch mode | Anti-429")
print("="*60)
for i,k in enumerate(API_KEYS):
    print(f"  Clé {i+1}: {mask(k)}")
print(f"  Discord: {'✅' if DISCORD_WH else '❌'} | GitHub: {'✅' if GH_TOKEN else '❌'}")
print(f"  Repo: {REPO_OWNER}/{REPO_NAME}")
print("="*60)

if not API_KEYS:
    print("FATAL: GEMINI_API_KEY manquante")
    sys.exit(1)

OS_MISSION = """MISSION: OS bare metal x86 complet type Windows 11.
PRIORITÉS: IDT+PIC → Timer PIT → Mémoire bitmap → VGA mode13h → Terminal → FAT12 → GUI → TCP/IP"""

RULES = """RÈGLES BARE METAL x86 ABSOLUES:
INTERDIT: #include<stddef.h|string.h|stdlib.h|stdio.h|stdint.h|stdbool.h>
INTERDIT: size_t NULL bool true false uint32_t uint8_t malloc memset strlen printf sprintf
REMPLACER: size_t→unsigned int | NULL→0 | bool→int | true→1 | false→0 | uint32_t→unsigned int | uint8_t→unsigned char
GCC: -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie
ASM: nasm -f elf (pour .o) | nasm -f bin (pour boot.bin)
LD: ld -m elf_i386 -T linker.ld --oformat binary
INTERDICTION ABSOLUE des commentaires dans le code (gaspillage de tokens)
Nouveaux fichiers .c OBLIGATOIRES dans Makefile
SIGNATURES IMPOSÉES: nb_init() nb_draw() nb_key(char k) | tm_init() tm_draw() tm_key(char k)
                     si_draw() ab_draw() | kb_init() kb_haskey() kb_getchar()
                     v_init() v_put() v_str() v_fill()
kernel_entry.asm DOIT définir _stack_top comme label global AVANT kernel_main"""

ALL_FILES = [
    "boot/boot.asm","kernel/kernel_entry.asm","kernel/kernel.c",
    "drivers/screen.h","drivers/screen.c","drivers/keyboard.h","drivers/keyboard.c",
    "ui/ui.h","ui/ui.c","apps/notepad.h","apps/notepad.c",
    "apps/terminal.h","apps/terminal.c","apps/sysinfo.h","apps/sysinfo.c",
    "apps/about.h","apps/about.c","Makefile","linker.ld",
]
SKIP_DIRS  = {".git","build","__pycache__",".github","ai_dev"}
SKIP_FILES = {"screen.h.save"}
SRC_EXTS   = {".c",".h",".asm",".ld"}

STANDARD_LABELS = {
    "ai-reviewed":"0075ca","ai-approved":"0e8a16","ai-rejected":"b60205",
    "needs-fix":"e4e669","bug":"d73a4a","enhancement":"a2eeef","stale":"eeeeee",
    "kernel":"5319e7","driver":"1d76db","app":"0052cc","documentation":"0075ca",
}

def get_key():
    now = time.time()
    n   = len(API_KEYS)
    for delta in range(n):
        idx = (KEY_STATE["idx"] + delta) % n
        if API_KEYS[idx] and now >= KEY_STATE["cooldowns"].get(idx, 0):
            KEY_STATE["idx"] = idx
            KEY_STATE["usage"][idx] = KEY_STATE["usage"].get(idx, 0) + 1
            return idx
    valid = [i for i in range(n) if API_KEYS[i]]
    if not valid:
        log("FATAL: aucune clé valide", "ERROR")
        sys.exit(1)
    best = min(valid, key=lambda i: KEY_STATE["cooldowns"].get(i, 0))
    wait = KEY_STATE["cooldowns"].get(best, 0) - now + 1
    log(f"Toutes clés en cooldown → attente {int(wait)}s", "TIME")
    disc_send_simple("⏳ Rate limit Gemini",
                     f"Toutes les clés en cooldown\nAttente: **{int(wait)}s**\nUptime: {uptime()}",
                     0xFF8800)
    time.sleep(max(wait, 1))
    KEY_STATE["idx"] = best
    return best

def set_cooldown(idx, secs):
    KEY_STATE["cooldowns"][idx] = time.time() + secs
    KEY_STATE["errors"][idx]    = KEY_STATE["errors"].get(idx, 0) + 1
    n   = len(API_KEYS)
    nxt = (idx + 1) % n
    for _ in range(n):
        if API_KEYS[nxt]: break
        nxt = (nxt + 1) % n
    KEY_STATE["idx"] = nxt
    log(f"Clé {idx+1} cooldown {secs}s → clé {nxt+1}", "WARN")

def key_status_str():
    now = time.time()
    lines = []
    for i in range(len(API_KEYS)):
        if not API_KEYS[i]: continue
        cd  = KEY_STATE["cooldowns"].get(i, 0)
        st  = "🟢 OK" if now >= cd else f"🔴 CD+{int(cd-now)}s"
        m   = ACTIVE_MODELS.get(i, {}).get("model", "?")
        c   = KEY_STATE["usage"].get(i, 0)
        tk  = KEY_STATE["tokens"].get(i, 0)
        lines.append(f"Clé {i+1}: {st} | {c} appels | ~{tk} tokens | {m}")
    return "\n".join(lines) or "Aucune clé"

def init_models():
    log("Init lazy des modèles...", "GEM")
    ok = 0
    for i in range(len(API_KEYS)):
        if not API_KEYS[i]: continue
        forbidden = KEY_STATE["forbidden"].get(i, set())
        for model in MODELS:
            if model not in forbidden:
                ACTIVE_MODELS[i] = {
                    "model": model,
                    "url":   (f"https://generativelanguage.googleapis.com"
                              f"/v1beta/models/{model}:generateContent?key={API_KEYS[i]}")
                }
                log(f"Clé {i+1} → {model}", "GEM")
                ok += 1
                break
    log(f"{ok}/{len(API_KEYS)} clés configurées", "GEM")
    return ok > 0

def find_model(idx):
    if idx >= len(API_KEYS) or not API_KEYS[idx]:
        return False
    key      = API_KEYS[idx]
    forbidden = KEY_STATE["forbidden"].get(idx, set())
    for model in MODELS:
        if model in forbidden:
            continue
        url     = (f"https://generativelanguage.googleapis.com/v1beta/models/"
                   f"{model}:generateContent?key={key}")
        payload = json.dumps({
            "contents": [{"parts":[{"text":"Reply OK"}]}],
            "generationConfig": {"maxOutputTokens":5,"temperature":0.0}
        }).encode()
        req = urllib.request.Request(url, data=payload,
                                     headers={"Content-Type":"application/json"},
                                     method="POST")
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read())
                if extract_text(data) is not None:
                    ACTIVE_MODELS[idx] = {"model": model, "url": url}
                    log(f"Clé {idx+1} → {model} (testé OK)", "GEM")
                    return True
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                forbidden.add(model)
                KEY_STATE["forbidden"][idx] = forbidden
            elif e.code == 429:
                time.sleep(5)
        except Exception:
            pass
        time.sleep(0.5)
    log(f"Clé {idx+1}: aucun modèle disponible", "WARN")
    return False

def extract_text(data):
    try:
        cands = data.get("candidates", [])
        if not cands:
            return None
        c      = cands[0]
        finish = c.get("finishReason","STOP")
        if finish in ("SAFETY","RECITATION"):
            return None
        parts = c.get("content",{}).get("parts",[])
        texts = [p.get("text","") for p in parts
                 if isinstance(p, dict) and not p.get("thought") and p.get("text")]
        result = "".join(texts)
        return result if result else None
    except Exception:
        return None

def gemini(prompt, max_tokens=32768, timeout=120, tag="?"):
    if not ACTIVE_MODELS:
        if not init_models():
            return None

    if len(prompt) > 55000:
        prompt = prompt[:55000] + "\n[TRONQUÉ]"

    payload = json.dumps({
        "contents": [{"parts":[{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature":     0.05,
        }
    }).encode("utf-8")

    max_attempts = len(API_KEYS) * 4
    t_global     = time.time()

    for attempt in range(1, max_attempts + 1):
        if not watchdog():
            return None

        idx        = get_key()
        model_info = ACTIVE_MODELS.get(idx)

        if not model_info:
            if not find_model(idx):
                set_cooldown(idx, 120)
                continue
            model_info = ACTIVE_MODELS.get(idx)

        url = model_info["url"].split("?")[0] + "?key=" + API_KEYS[idx]
        log(f"[{tag}] Clé {idx+1}/{model_info['model']} attempt={attempt}", "GEM")

        disc_log(f"🤖 Gemini [{tag}]",
                 f"Clé **{idx+1}** | `{model_info['model']}` | tentative **{attempt}**\n"
                 f"Uptime: `{uptime()}` | Rate limit restant: `{GH_RATE['remaining']}`",
                 0x5865F2)

        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type":"application/json"},
            method="POST"
        )

        try:
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw  = r.read().decode("utf-8")
                data = json.loads(raw)
            elapsed = round(time.time()-t0, 1)
            text    = extract_text(data)

            if text is None:
                log(f"[{tag}] Réponse vide/bloquée en {elapsed}s", "WARN")
                forbidden = KEY_STATE["forbidden"].setdefault(idx, set())
                forbidden.add(model_info["model"])
                if idx in ACTIVE_MODELS: del ACTIVE_MODELS[idx]
                find_model(idx)
                continue

            finish = ""
            try: finish = data["candidates"][0].get("finishReason","STOP")
            except Exception: pass

            est_tokens = len(text) // 4
            KEY_STATE["tokens"][idx] = KEY_STATE["tokens"].get(idx,0) + est_tokens

            log(f"[{tag}] ✅ {len(text)} chars en {elapsed}s (finish={finish}, ~{est_tokens}tk)", "GEM")
            disc_log(f"✅ Gemini OK [{tag}]",
                     f"{len(text):,} chars en **{elapsed}s**\n"
                     f"finish=`{finish}` | ~`{est_tokens}` tokens\n"
                     f"Clé **{idx+1}** | `{model_info['model']}`",
                     0x00FF88)
            return text

        except urllib.error.HTTPError as e:
            elapsed = round(time.time()-t0, 1)
            body    = ""
            try: body = e.read().decode()[:300]
            except: pass
            log(f"[{tag}] HTTP {e.code} en {elapsed}s: {body[:80]}", "WARN")

            disc_log(f"⚠️ Gemini HTTP {e.code} [{tag}]",
                     f"Clé **{idx+1}** | `{model_info['model']}`\n"
                     f"Code: `{e.code}` | Durée: `{elapsed}s`\n"
                     f"`{body[:150]}`",
                     0xFF4400)

            if e.code == 429:
                errs = KEY_STATE["errors"].get(idx, 0)
                wait = min(60 * (errs + 1), 180)
                set_cooldown(idx, wait)
                now = time.time()
                autre_dispo = any(
                    API_KEYS[i] and now >= KEY_STATE["cooldowns"].get(i,0)
                    for i in range(len(API_KEYS)) if i != idx
                )
                if not autre_dispo:
                    sleep_t = min(wait, 60)
                    log(f"Pause {sleep_t}s (toutes clés busy)", "TIME")
                    time.sleep(sleep_t)
            elif e.code == 403:
                forbidden = KEY_STATE["forbidden"].setdefault(idx, set())
                forbidden.add(model_info["model"])
                if idx in ACTIVE_MODELS: del ACTIVE_MODELS[idx]
                if not find_model(idx):
                    set_cooldown(idx, 600)
            elif e.code in (400, 404):
                if idx in ACTIVE_MODELS: del ACTIVE_MODELS[idx]
                find_model(idx)
            elif e.code == 500:
                time.sleep(20)
            else:
                time.sleep(10)

        except TimeoutError:
            log(f"[{tag}] TIMEOUT {timeout}s", "WARN")
            KEY_STATE["idx"] = (idx+1) % len(API_KEYS)
        except Exception as ex:
            log(f"[{tag}] Exception: {ex}", "ERROR")
            if DEBUG: traceback.print_exc()
            time.sleep(10)

    log(f"[{tag}] ÉCHEC total après {max_attempts} tentatives", "ERROR")
    return None

def disc_raw(embeds):
    if not DISCORD_WH:
        return False
    payload = json.dumps({
        "username": "MaxOS AI v" + VERSION,
        "embeds":   embeds[:10]
    }).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WH, data=payload,
        headers={"Content-Type":"application/json","User-Agent":"MaxOS-Bot"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status in (200, 204)
    except Exception as ex:
        log(f"Discord: {ex}", "WARN")
        return False

def make_embed(title, desc, color, fields=None):
    now     = time.time()
    active  = sum(1 for i in range(len(API_KEYS))
                  if API_KEYS[i] and now >= KEY_STATE["cooldowns"].get(i,0))
    model   = ACTIVE_MODELS.get(KEY_STATE["idx"],{}).get("model","?")
    total_t = sum(KEY_STATE["tokens"].values())
    e = {
        "title":       str(title)[:256],
        "description": str(desc)[:4096],
        "color":       color,
        "timestamp":   datetime.utcnow().isoformat() + "Z",
        "footer": {"text": (
            f"MaxOS AI v{VERSION} | {model} | {active}/{len(API_KEYS)} clés | "
            f"uptime {uptime()} | ~{total_t}tk | RL:{GH_RATE['remaining']}"
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

DISC_LOG_BUFFER    = []
DISC_LOG_LAST_SEND = 0
DISC_LOG_INTERVAL  = 30

def disc_log(title, desc, color=0x5865F2):
    DISC_LOG_BUFFER.append((title, desc, color, time.time()))
    flush_disc_log(force=False)

def flush_disc_log(force=True):
    global DISC_LOG_LAST_SEND
    now = time.time()
    if not force and now - DISC_LOG_LAST_SEND < DISC_LOG_INTERVAL:
        return
    if not DISC_LOG_BUFFER:
        return
    embeds = []
    while DISC_LOG_BUFFER and len(embeds) < 10:
        title, desc, color, _ = DISC_LOG_BUFFER.pop(0)
        embeds.append(make_embed(title, desc, color))
    if embeds:
        disc_raw(embeds)
        DISC_LOG_LAST_SEND = now

def disc_send_simple(title, desc, color=0x5865F2, fields=None):
    flush_disc_log(force=True)
    disc_raw([make_embed(title, desc, color, fields)])

def disc_send_task_start(i, total, nom, priorite, cat, desc):
    pct = int((i-1)/total*100)
    disc_send_simple(
        f"🚀 [{i}/{total}] {nom[:60]}",
        f"```\n{pbar(pct)}\n```\n{desc[:200]}",
        0xFFA500,
        [{"name":"Priorité","value":priorite,"inline":True},
         {"name":"Catégorie","value":cat,"inline":True},
         {"name":"Uptime","value":uptime(),"inline":True},
         {"name":"Rate limit","value":str(GH_RATE["remaining"]),"inline":True},
         {"name":"Clés","value":key_status_str(),"inline":False}]
    )

def disc_send_task_ok(i, total, nom, sha, written, deleted, elapsed, fix_count):
    pct = int(i/total*100)
    files_str = "\n".join(f"`{f}`" for f in (written+deleted)[:8]) or "aucun"
    fix_str   = f" (après **{fix_count}** fix)" if fix_count else ""
    disc_send_simple(
        f"✅ [{i}/{total}] {nom[:55]} OK{fix_str}",
        f"```\n{pbar(pct)}\n```\nCommit: `{sha}`",
        0x00FF88,
        [{"name":"⏱️ Temps","value":f"{elapsed:.0f}s","inline":True},
         {"name":"📁 Fichiers","value":str(len(written+deleted)),"inline":True},
         {"name":"🎯 Progress","value":pbar(pct),"inline":False},
         {"name":"📝 Modifiés","value":files_str,"inline":False}]
    )

def disc_send_task_fail(i, total, nom, reason, errors, elapsed):
    errs_str = "\n".join(f"• {e[:80]}" for e in errors[:5]) or "?"
    disc_send_simple(
        f"❌ [{i}/{total}] {nom[:55]} ÉCHEC",
        f"Raison: `{reason}` | Durée: `{elapsed:.0f}s`",
        0xFF4444,
        [{"name":"🔴 Erreurs","value":errs_str[:900],"inline":False},
         {"name":"🔑 Clés","value":key_status_str(),"inline":False},
         {"name":"⏱️ Uptime","value":uptime(),"inline":True}]
    )

def disc_send_build_status(ok, errs, elapsed):
    if ok:
        disc_log("🔨 Build OK", f"Compilation réussie en `{elapsed:.1f}s`", 0x00CC44)
    else:
        err_str = "\n".join(f"• `{e[:80]}`" for e in errs[:6])
        disc_log(f"🔨 Build ÉCHEC ({len(errs)} erreur(s))",
                 f"Durée: `{elapsed:.1f}s`\n{err_str}", 0xFF2200)

def disc_send_fix_attempt(attempt, max_a, n_errs):
    disc_log(f"🔧 Auto-fix tentative {attempt}/{max_a}",
             f"`{n_errs}` erreur(s) à corriger", 0x00AAFF)

def disc_send_heartbeat(current_task, total, status_msg):
    disc_log(f"💓 Heartbeat | Tâche {current_task}/{total}",
             f"{status_msg}\nUptime: `{uptime()}` | Clés: {key_status_str()}",
             0x7289DA)

def gh_api(method, endpoint, data=None, raw_url=None, retry=3):
    if not GH_TOKEN:
        return None
    url     = raw_url or f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/{endpoint}"
    payload = json.dumps(data).encode() if data else None
    for attempt in range(1, retry+1):
        req = urllib.request.Request(
            url, data=payload,
            headers={
                "Authorization":        "Bearer " + GH_TOKEN,
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
            log(f"GitHub {method} {endpoint} HTTP {e.code}: {body[:100]}", "WARN")
            if e.code in (500,502,503,504) and attempt < retry:
                time.sleep(5*attempt); continue
            if e.code == 403 and "rate limit" in body.lower():
                wait = max(GH_RATE["reset"] - time.time() + 5, 60)
                log(f"GitHub rate limit → attente {int(wait)}s", "WARN")
                time.sleep(wait); continue
            return None
        except Exception as ex:
            log(f"GitHub {method} {endpoint}: {ex}", "ERROR")
            if attempt < retry: time.sleep(3); continue
            return None
    return None

def gh_get_all(endpoint, per_page=100):
    results = []
    page    = 1
    while True:
        sep = "&" if "?" in endpoint else "?"
        r   = gh_api("GET", f"{endpoint}{sep}per_page={per_page}&page={page}")
        if not isinstance(r, list) or not r: break
        results.extend(r)
        if len(r) < per_page: break
        page += 1
    return results

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

def gh_merge(num, title):
    r = gh_api("PUT",f"pulls/{num}/merge",{
        "commit_title":f"merge: {title} [AI]","merge_method":"squash"})
    return bool(r and r.get("merged"))

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
    created  = 0
    for name, color in desired.items():
        if name not in existing:
            gh_api("POST","labels",{"name":name,"color":color,"description":f"[MaxOS AI] {name}"})
            log(f"Label créé: {name}", "NET")
            created += 1
    return created

def gh_list_milestones():
    r = gh_api("GET","milestones?state=open&per_page=30")
    return r if isinstance(r,list) else []

def gh_ensure_milestone(title):
    for m in gh_list_milestones():
        if m.get("title") == title:
            return m.get("number")
    r = gh_api("POST","milestones",{"title":title,"description":f"[MaxOS AI] {title}"})
    return r.get("number") if r else None

def gh_assign_milestone(issue_num, ms_num):
    gh_api("PATCH",f"issues/{issue_num}",{"milestone":ms_num})

def gh_list_releases(n=10):
    r = gh_api("GET",f"releases?per_page={n}")
    return r if isinstance(r,list) else []

def gh_create_release(tag, name, body, pre=False):
    r = gh_api("POST","releases",{
        "tag_name":tag,"name":name,"body":body,
        "draft":False,"prerelease":pre
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
    return r.returncode == 0, r.stdout, r.stderr

def get_sha():
    _, sha, _ = git_cmd(["rev-parse","HEAD"])
    return sha.strip()[:40]

def git_push(task_name, files, description, model):
    if not files:
        return True, None, None
    dirs   = set(f.split("/")[0] for f in files if "/" in f)
    pmap   = {"kernel":"kernel","drivers":"driver","boot":"boot",
               "ui":"ui","apps":"feat(apps)","lib":"lib"}
    prefix = next((pmap[d] for d in pmap if d in dirs), "feat")
    fshort = ", ".join(os.path.basename(f) for f in files[:3])
    if len(files) > 3: fshort += f" +{len(files)-3}"
    short  = f"{prefix}: {task_name[:50]} [{fshort}]"
    body   = (f"\n\nFiles: {', '.join(files)}\nModel: {model}\n"
              f"Time: {datetime.utcnow().isoformat()}Z\nArch: x86-32 bare metal")
    git_cmd(["add","-A"])
    ok, out, err = git_cmd(["commit","-m",short+body])
    if not ok:
        if "nothing to commit" in (out+err):
            log("Rien à committer", "GIT")
            return True, None, None
        log(f"Commit KO: {err[:200]}", "ERROR")
        return False, None, None
    _, sha, _ = git_cmd(["rev-parse","HEAD"])
    sha        = sha.strip()[:7]
    ok2, _, e2 = git_cmd(["push"])
    if not ok2:
        git_cmd(["pull","--rebase"])
        ok2, _, e2 = git_cmd(["push"])
        if not ok2:
            log(f"Push KO: {e2[:200]}", "ERROR")
            return False, None, None
    log(f"Push OK: {sha} — {short}", "GIT")
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
            seen.add(s)
            unique.append(s[:120])
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
    log(f"Build {'OK' if ok else 'ÉCHEC'} en {elapsed}s ({len(errs)} erreur(s))", "BUILD")
    for e in errs[:3]:
        log(f"  >> {e[:100]}", "BUILD")
    disc_send_build_status(ok, errs, elapsed)
    return ok, log_text, errs

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
        if os.path.exists(p):
            h.update(str(os.path.getmtime(p)).encode())
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

def build_context(sources, max_chars=40000):
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
        block = f"{'='*50}\nFICHIER: {f}\n{'='*50}\n{c}\n\n"
        if used+len(block) > max_chars: continue
        ctx += block; used += len(block); done.add(f)
    for f,c in sources.items():
        if f in done or not c: continue
        block = f"{'='*50}\nFICHIER: {f}\n{'='*50}\n{c}\n\n"
        if used+len(block) > max_chars:
            ctx += f"[{f} tronqué]\n"
            continue
        ctx += block; used += len(block)
    return ctx

def proj_stats(sources):
    files = sum(1 for c in sources.values() if c)
    lines = sum(c.count("\n") for c in sources.values() if c)
    chars = sum(len(c) for c in sources.values() if c)
    return {"files":files,"lines":lines,"chars":chars}

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
                        violations.append(f"{fname}:{i} include interdit: {inc}")
                for sym in forbidden_sym:
                    if re.search(r'\b'+re.escape(sym)+r'\b', line):
                        violations.append(f"{fname}:{i} symbole interdit: {sym}")
                        break
        elif fname.endswith(".asm"):
            asm_files   += 1
            total_lines += content.count("\n")
    score = max(0, 100 - len(violations)*5)
    return {"score":score,"violations":violations[:20],"c_files":c_files,
            "asm_files":asm_files,"total_lines":total_lines}

def parse_files(response):
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
                for lang in ["```c","```asm","```nasm","```makefile","```ld","```bash","```text","```"]:
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
        log(f"Parse: rien trouvé. Début: {response[:200]}", "WARN")
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
            os.remove(full)
            deleted.append(path)
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
                "nom": "IDT 256 entrées + PIC 8259 + handlers",
                "priorite":"CRITIQUE","categorie":"kernel",
                "fichiers_a_modifier":["kernel/kernel.c","kernel/kernel_entry.asm","Makefile"],
                "fichiers_a_creer":["kernel/idt.h","kernel/idt.c"],
                "fichiers_a_supprimer":[],
                "description":(
                    "kernel_entry.asm: définir _stack_top comme label global, "
                    "pile 16KB, multiboot header complet. "
                    "idt.h: struct IDTEntry packed, struct IDTPointer. "
                    "idt.c: idt_set_gate(), idt_init(), PIC 8259 remappage "
                    "IRQ0-7→0x20-0x27 IRQ8-15→0x28-0x2F, stubs extern ASM vecteurs 0-47, "
                    "isr_handler() irq_handler() avec outb EOI, panic() écran rouge, sti()."
                ),
                "impact_attendu":"OS stable sans triple fault",
                "complexite":"HAUTE"
            },
            {
                "nom": "Timer PIT 8253 100Hz + uptime + sleep_ms",
                "priorite":"CRITIQUE","categorie":"kernel",
                "fichiers_a_modifier":["kernel/kernel.c","Makefile"],
                "fichiers_a_creer":["kernel/timer.h","kernel/timer.c"],
                "fichiers_a_supprimer":[],
                "description":(
                    "timer.h: timer_init() timer_ticks() sleep_ms(unsigned int ms). "
                    "timer.c: PIT canal 0 diviseur 11931=100Hz, outb 0x43/0x40, "
                    "volatile unsigned int ticks, IRQ0 handler, uptime HH:MM:SS."
                ),
                "impact_attendu":"Horloge système visible",
                "complexite":"MOYENNE"
            },
            {
                "nom": "Terminal 20 commandes + historique",
                "priorite":"HAUTE","categorie":"app",
                "fichiers_a_modifier":["apps/terminal.h","apps/terminal.c"],
                "fichiers_a_creer":[],
                "fichiers_a_supprimer":[],
                "description":(
                    "20 commandes: help ver mem uptime cls echo date reboot halt "
                    "color beep calc snake pong about credits clear ps sysinfo license. "
                    "Historique 20 entrées, flèche haut/bas. ZERO stdlib."
                ),
                "impact_attendu":"Terminal complet",
                "complexite":"MOYENNE"
            },
            {
                "nom": "Allocateur mémoire bitmap 4KB",
                "priorite":"HAUTE","categorie":"kernel",
                "fichiers_a_modifier":["kernel/kernel.c","Makefile"],
                "fichiers_a_creer":["kernel/memory.h","kernel/memory.c"],
                "fichiers_a_supprimer":[],
                "description":(
                    "Bitmap 32MB/4KB=8192 bits dans tableau unsigned int. "
                    "mem_init(unsigned int start, unsigned int end) "
                    "mem_alloc() → unsigned int addr, mem_free(unsigned int addr). "
                    "ZERO malloc ZERO NULL → utiliser 0."
                ),
                "impact_attendu":"Allocation mémoire fonctionnelle",
                "complexite":"HAUTE"
            },
            {
                "nom": "VGA mode 13h 320x200 + desktop",
                "priorite":"NORMALE","categorie":"driver",
                "fichiers_a_modifier":["drivers/screen.h","drivers/screen.c","kernel/kernel.c","Makefile"],
                "fichiers_a_creer":["drivers/vga.h","drivers/vga.c"],
                "fichiers_a_supprimer":[],
                "description":(
                    "vga.h: v_init() v_pixel(int x,int y,unsigned char c) "
                    "v_rect() v_fill() v_line(). "
                    "vga.c: outb 0x3C8/0x3C9 mode 13h, framebuffer 0xA0000. "
                    "Desktop bleu + taskbar grise bas."
                ),
                "impact_attendu":"Interface graphique 256 couleurs",
                "complexite":"HAUTE"
            }
        ]
    }

def phase_analyse(context, stats):
    log("\n=== PHASE 1: ANALYSE ===")
    disc_send_simple("🔍 Phase 1: Analyse du projet",
                     f"Analyse de `{stats['files']}` fichiers, `{stats['lines']}` lignes...",
                     0x5865F2)
    prompt = (
        f"Expert OS bare metal x86.\n{RULES}\n{OS_MISSION}\n\n"
        f"{context}\n\n"
        f"STATS: {stats['files']} fichiers, {stats['lines']} lignes\n\n"
        "JSON UNIQUEMENT (commence par {):\n"
        '{"score_actuel":35,"niveau_os":"Prototype","fonctionnalites_presentes":["Boot"],'
        '"fonctionnalites_manquantes_critiques":["IDT"],'
        '"plan_ameliorations":[{"nom":"IDT","priorite":"CRITIQUE","categorie":"kernel",'
        '"fichiers_a_modifier":["kernel/kernel.c"],"fichiers_a_creer":["kernel/idt.h"],'
        '"fichiers_a_supprimer":[],"description":"...","impact_attendu":"...","complexite":"HAUTE"}],'
        '"prochaine_milestone":"Kernel stable"}'
    )
    resp = gemini(prompt, max_tokens=3000, timeout=60, tag="analyse")
    if not resp:
        log("Analyse Gemini KO → plan par défaut", "WARN")
        return default_plan()
    log(f"Analyse: {len(resp)} chars reçus")
    clean = resp.strip()
    if clean.startswith("```"):
        lines = clean.split("\n")[1:]
        if lines and lines[-1].strip() == "```": lines = lines[:-1]
        clean = "\n".join(lines).strip()
    clean = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', clean)
    for _ in range(3):
        i = clean.find("{"); j = clean.rfind("}")+1
        if i >= 0 and j > i:
            try:
                result = json.loads(clean[i:j])
                log(f"Analyse OK: score={result.get('score_actuel','?')} | "
                    f"{len(result.get('plan_ameliorations',[]))} tâches")
                return result
            except json.JSONDecodeError as e:
                log(f"JSON err: {e}", "WARN")
                clean = clean[i+1:]
    log("JSON parse impossible → plan par défaut", "WARN")
    return default_plan()

def build_task_context(task, all_sources):
    f_mod  = task.get("fichiers_a_modifier",[])
    f_new  = task.get("fichiers_a_creer",[])
    needed = set(f_mod + f_new)
    for f in list(needed):
        partner = f.replace(".c",".h") if f.endswith(".c") else f.replace(".h",".c")
        if partner in all_sources: needed.add(partner)
    for ess in ["kernel/kernel.c","kernel/kernel_entry.asm","Makefile","linker.ld",
                "drivers/screen.h","drivers/keyboard.h"]:
        needed.add(ess)
    ctx       = ""
    total_len = 0
    for f in sorted(needed):
        c     = all_sources.get(f,"")
        block = f"--- {f} ---\n{c if c else '[À CRÉER]'}\n\n"
        if total_len + len(block) > 20000:
            ctx += f"[{f} tronqué]\n"
            continue
        ctx       += block
        total_len += len(block)
    return ctx

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
        f"TÂCHE: {nom} | CAT: {cat} | CX: {cx}\n"
        f"MODIFIER: {f_mod}\n"
        f"CRÉER: {f_new}\n"
        f"SUPPRIMER: {f_del}\n"
        f"SPECS: {desc}\n\n"
        f"CODE EXISTANT:\n{ctx}\n\n"
        "RÈGLES OUTPUT:\n"
        "- Code 100% complet, ZERO commentaire, ZERO '...', ZERO placeholder\n"
        "- ZERO include stdlib, ZERO NULL, ZERO bool, ZERO uint32_t\n"
        "- kernel_entry.asm: _stack_top label global défini AVANT kernel_main\n"
        "- Chaque nouveau .c DOIT être dans Makefile OBJS\n"
        "- Supprimer: === DELETE: chemin ===\n\n"
        "FORMAT STRICT:\n"
        "=== FILE: chemin/fichier.ext ===\n"
        "[code complet sans commentaires]\n"
        "=== END FILE ===\n\n"
        "GÉNÈRE MAINTENANT:"
    )

def auto_fix(build_log_text, errs, gen_files, bak, model, max_attempts=3):
    log(f"Auto-fix: {len(errs)} erreur(s)", "BUILD")
    current_log  = build_log_text
    current_errs = errs
    for attempt in range(1, max_attempts+1):
        log(f"Fix tentative {attempt}/{max_attempts}", "BUILD")
        disc_send_fix_attempt(attempt, max_attempts, len(current_errs))
        curr = {}
        for p in gen_files:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp):
                with open(fp,"r") as f:
                    curr[p] = f.read()[:8000]
        ctx     = "".join(f"--- {p} ---\n{c}\n\n" for p,c in curr.items())
        err_str = "\n".join(current_errs[:10])
        prompt  = (
            f"{RULES}\n\n"
            "ERREURS DE COMPILATION:\n"
            f"```\n{err_str}\n```\n\n"
            f"LOG (fin):\n```\n{current_log[-1500:]}\n```\n\n"
            f"FICHIERS ACTUELS:\n{ctx}\n\n"
            "CORRIGE TOUTES LES ERREURS.\n"
            "RÈGLES: ZERO commentaire, ZERO stdlib, ZERO NULL→0, "
            "ZERO bool→int, _stack_top DOIT être défini comme label global dans kernel_entry.asm\n"
            "FORMAT:\n=== FILE: fichier.ext ===\n[code]\n=== END FILE ==="
        )
        resp = gemini(prompt, max_tokens=24576, timeout=90, tag=f"fix/{attempt}")
        if not resp:
            continue
        files, _ = parse_files(resp)
        if not files:
            log("Fix: rien parsé", "WARN")
            continue
        write_files(files)
        ok, current_log, current_errs = make_build()
        if ok:
            all_fixed = list(files.keys())
            git_push("fix: corrections compilation", all_fixed,
                     f"Auto-fix: {len(errs)} erreurs → 0", model)
            disc_send_simple("🔧 Auto-fix réussi",
                             f"{len(errs)} erreur(s) corrigée(s) en {attempt} tentative(s).",
                             0x00AAFF)
            return True, {"attempts": attempt}
        log(f"Fix {attempt}: {len(current_errs)} erreur(s) restante(s)", "WARN")
        time.sleep(8)
    restore_files(bak)
    return False, {"attempts": max_attempts}

def phase_implement_one(task, all_sources, i, total):
    nom   = task.get("nom","?")
    cat   = task.get("categorie","general")
    cx    = task.get("complexite","MOYENNE")
    desc  = task.get("description","")
    f_mod = task.get("fichiers_a_modifier",[])
    f_new = task.get("fichiers_a_creer",[])
    f_del = task.get("fichiers_a_supprimer",[])
    model = ACTIVE_MODELS.get(KEY_STATE["idx"],{}).get("model","?")

    log(f"\n{'='*60}")
    log(f"[{i}/{total}] {nom}")
    log(f"  Cat={cat} Cx={cx} Mod={f_mod} New={f_new}")
    log(f"{'='*60}")

    disc_send_task_start(i, total, nom, task.get("priorite","?"), cat, desc)

    t_start = time.time()
    targets = list(set(f_mod + f_new))
    ctx     = build_task_context(task, all_sources)
    tok_map = {"HAUTE":32768,"MOYENNE":20480,"BASSE":12288}
    max_tok = tok_map.get(cx, 20480)
    prompt  = build_impl_prompt(task, ctx)

    disc_log(f"⏳ Gemini génère [{nom[:40]}]",
             f"Prompt: `{len(prompt):,}` chars | Max tokens: `{max_tok}`\n"
             f"Fichiers cibles: {', '.join(f'`{f}`' for f in targets[:5])}", 0xFFA500)

    resp    = gemini(prompt, max_tokens=max_tok, timeout=150, tag=f"impl/{nom[:20]}")
    elapsed = round(time.time()-t_start, 1)

    if not resp:
        disc_send_task_fail(i, total, nom, "gemini_fail", [], elapsed)
        return False, [], [], {"nom":nom,"elapsed":elapsed,"result":"gemini_fail","errors":[]}

    log(f"Réponse: {len(resp)} chars en {elapsed}s")
    disc_log(f"📄 Réponse reçue [{nom[:40]}]",
             f"`{len(resp):,}` chars en `{elapsed}s`\nParsing des fichiers...", 0x5865F2)

    files, to_del = parse_files(resp)

    if not files and not to_del:
        disc_send_task_fail(i, total, nom, "parse_empty", [], elapsed)
        return False, [], [], {"nom":nom,"elapsed":elapsed,"result":"parse_empty","errors":[]}

    disc_log(f"📁 {len(files)} fichier(s) à écrire",
             "\n".join(f"`{f}` ({len(c):,} chars)" for f,c in list(files.items())[:8]),
             0x00AAFF)

    bak     = backup_files(list(files.keys()))
    written = write_files(files)
    deleted = delete_files(to_del)

    if not written and not deleted:
        disc_send_task_fail(i, total, nom, "no_files", [], elapsed)
        return False, [], [], {"nom":nom,"elapsed":elapsed,"result":"no_files","errors":[]}

    ok, build_log_text, errs = make_build()

    if ok:
        pushed, sha, _ = git_push(nom, written+deleted, desc, model)
        if pushed:
            metrics = {"nom":nom,"elapsed":round(time.time()-t_start,1),
                       "result":"success","sha":sha,"files":written+deleted,"model":model,"fix_count":0}
            disc_send_task_ok(i, total, nom, sha or "?", written, deleted,
                              metrics["elapsed"], 0)
            return True, written, deleted, metrics
        restore_files(bak)
        disc_send_task_fail(i, total, nom, "push_fail", [], elapsed)
        return False, [], [], {"nom":nom,"elapsed":elapsed,"result":"push_fail","errors":[]}

    fixed, fix_metrics = auto_fix(build_log_text, errs, list(files.keys()), bak, model)
    if fixed:
        metrics = {"nom":nom,"elapsed":round(time.time()-t_start,1),
                   "result":"success_after_fix","files":written+deleted,
                   "model":model,"fix_count":fix_metrics.get("attempts",0),"sha":"fixed"}
        disc_send_task_ok(i, total, nom, "fixed", written, deleted,
                          metrics["elapsed"], metrics["fix_count"])
        return True, written, deleted, metrics

    restore_files(bak)
    for p in written:
        if p not in bak:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp): os.remove(fp)
    SOURCE_CACHE["hash"] = None
    disc_send_task_fail(i, total, nom, "build_fail", errs, round(time.time()-t_start,1))
    return False, [], [], {"nom":nom,"elapsed":round(time.time()-t_start,1),
                           "result":"build_fail","errors":errs[:5]}

def batch_analyse_and_plan(sources, stats):
    """
    Appel UNIQUE Gemini qui analyse ET génère le plan complet.
    Évite un appel séparé pour l'analyse.
    """
    return phase_analyse(build_context(sources), stats)

def handle_issues():
    issues = gh_open_issues()
    if not issues:
        log("Issues: aucune ouverte")
        return
    log(f"Issues: {len(issues)} à traiter")
    gh_ensure_labels(STANDARD_LABELS)
    bot_logins = {"MaxOS-AI-Bot","github-actions[bot]"}
    for issue in issues[:8]:
        num    = issue.get("number")
        title  = issue.get("title","")
        author = issue.get("user",{}).get("login","")
        if author in bot_logins: continue
        timeline = gh_issue_timeline(num)
        already  = any(
            e.get("actor",{}).get("login","") in bot_logins or
            e.get("user",{}).get("login","") in bot_logins
            for e in (timeline or [])
        )
        if already: continue
        log(f"Issue #{num}: {title[:50]} par {author}")
        prompt = (
            f"Bot de gestion d'issues OS bare metal x86 MaxOS.\n"
            f"ISSUE #{num}: {title}\nAuteur: {author}\n"
            f"Corps: {(issue.get('body','') or '')[:800]}\n\n"
            "JSON UNIQUEMENT:\n"
            '{"type":"bug|enhancement|question|invalid","priority":"high|medium|low",'
            '"labels":["bug"],"action":"respond|close|label_only",'
            '"close_reason":"completed|not_planned",'
            '"response":"réponse en français courte et utile"}'
        )
        resp = gemini(prompt, max_tokens=1024, timeout=30, tag=f"issue/{num}")
        if not resp: continue
        clean = resp.strip()
        if clean.startswith("```"):
            lines = clean.split("\n")[1:]
            if lines and lines[-1].strip()=="```": lines=lines[:-1]
            clean = "\n".join(lines).strip()
        try:
            i = clean.find("{"); j = clean.rfind("}")+1
            if i >= 0 and j > i:
                analysis = json.loads(clean[i:j])
                action   = analysis.get("action","label_only")
                labels   = [l for l in analysis.get("labels",[]) if l in STANDARD_LABELS]
                response = analysis.get("response","")
                itype    = analysis.get("type","?")
                if labels: gh_add_labels(num, labels)
                if response and action in ("respond","close","close_not_planned"):
                    icon = {"bug":"🐛","enhancement":"✨","question":"❓"}.get(itype,"💬")
                    gh_comment(num, (
                        f"{icon} **MaxOS AI** — Réponse automatique\n\n{response}\n\n"
                        f"---\n*MaxOS AI v{VERSION} | {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC*"
                    ))
                if action == "close":
                    gh_close_issue(num, "completed")
                elif action == "close_not_planned":
                    gh_close_issue(num, "not_planned")
                disc_log(f"🎫 Issue #{num} traitée",
                         f"**{title[:50]}** | Type: `{itype}` | Action: `{action}`", 0x00FF88)
                log(f"Issue #{num} → {action} ({itype})")
        except Exception as ex:
            log(f"Issue #{num} parse err: {ex}", "WARN")
        time.sleep(1.5)

def handle_stale_issues(days_stale=21, days_close=7):
    issues  = gh_open_issues()
    now     = time.time()
    stale_s = days_stale * 86400
    close_s = (days_stale + days_close) * 86400
    staled  = 0
    closed  = 0
    for issue in issues:
        num        = issue.get("number")
        updated_at = issue.get("updated_at","")
        labels     = [l.get("name","") for l in issue.get("labels",[])]
        is_stale   = "stale" in labels
        try:
            updated_ts = datetime.strptime(updated_at,"%Y-%m-%dT%H:%M:%SZ").timestamp()
        except: continue
        age = now - updated_ts
        if age >= close_s and is_stale:
            gh_comment(num,
                "🤖 **MaxOS AI**: Issue fermée automatiquement (inactive "
                f"{int(age/86400)} jours).\nRouvrez si le problème persiste.")
            gh_close_issue(num, "not_planned")
            closed += 1
        elif age >= stale_s and not is_stale:
            gh_add_labels(num, ["stale"])
            gh_comment(num,
                f"⏰ **MaxOS AI**: Aucune activité depuis {int(age/86400)} jours. "
                f"Fermeture dans **{days_close} jours** sans réponse.")
            staled += 1
    if staled + closed > 0:
        log(f"Stale: {staled} marquées, {closed} fermées")

def handle_prs():
    prs = gh_open_prs()
    if not prs:
        log("PRs: aucune ouverte")
        return
    log(f"PRs: {len(prs)} à traiter")
    bot_logins = {"MaxOS-AI-Bot","github-actions[bot]"}
    for pr in prs[:5]:
        num    = pr.get("number")
        title  = pr.get("title","")
        author = pr.get("user",{}).get("login","")
        if author in bot_logins: continue
        existing = gh_pr_reviews(num)
        if any(r.get("user",{}).get("login","") in bot_logins for r in (existing or [])):
            continue
        log(f"PR #{num}: {title[:50]}")
        files_data = gh_pr_files(num)
        commits    = gh_pr_commits(num)
        file_list  = "\n".join(
            f"- {f.get('filename','?')} (+{f.get('additions',0)} -{f.get('deletions',0)})"
            for f in files_data[:15]
        )
        patches = ""
        for f in [x for x in files_data if any(
            x.get("filename","").endswith(e) for e in [".c",".h",".asm"])][:4]:
            patches += f"\n--- {f.get('filename','?')} ---\n{f.get('patch','')[:1000]}\n"
        prompt = (
            f"Expert OS bare metal x86. Code review de PR.\n{RULES}\n\n"
            f"PR #{num}: {title}\nAuteur: {author}\n"
            f"Description: {(pr.get('body','') or '')[:400]}\n\n"
            f"FICHIERS:\n{file_list}\n\nCHANGEMENTS:\n{patches}\n\n"
            "JSON UNIQUEMENT:\n"
            '{"decision":"APPROVE|REQUEST_CHANGES|COMMENT",'
            '"summary":"résumé 2 phrases","problems":["prob1"],'
            '"positives":["point1"],"merge_safe":true,'
            '"bare_metal_violations":["viol1"]}'
        )
        resp = gemini(prompt, max_tokens=2048, timeout=45, tag=f"pr/{num}")
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
                violations = a.get("bare_metal_violations",[])
                icon       = {"APPROVE":"✅","REQUEST_CHANGES":"🔴","COMMENT":"💬"}.get(decision,"💬")
                body       = (
                    f"## {icon} Code Review MaxOS AI — PR #{num}\n\n"
                    f"> **Décision**: `{decision}` | **Safe**: {'🟢' if merge_safe else '🔴'}\n\n"
                    f"{summary}\n\n"
                )
                if problems:   body += "### ❌ Problèmes\n" + "\n".join(f"- {p}" for p in problems) + "\n\n"
                if positives:  body += "### ✅ Positifs\n"  + "\n".join(f"- {p}" for p in positives) + "\n\n"
                if violations: body += "### ⚠️ Violations bare metal\n" + "\n".join(f"- `{v}`" for v in violations) + "\n\n"
                body += f"\n---\n*MaxOS AI v{VERSION} | {ACTIVE_MODELS.get(KEY_STATE['idx'],{}).get('model','?')}*"
                if decision == "APPROVE" and merge_safe:
                    gh_post_review(num, body, "APPROVE")
                    gh_add_labels(num, ["ai-approved","ai-reviewed"])
                elif decision == "REQUEST_CHANGES":
                    gh_post_review(num, body, "REQUEST_CHANGES")
                    gh_add_labels(num, ["ai-rejected","ai-reviewed","needs-fix"])
                else:
                    gh_post_review(num, body, "COMMENT")
                    gh_add_labels(num, ["ai-reviewed"])
                disc_log(f"📋 PR #{num} reviewée",
                         f"**{title[:50]}**\nDécision: `{decision}` | Safe: {'✅' if merge_safe else '❌'}",
                         0x00AAFF if decision=="APPROVE" else 0xFF4444 if decision=="REQUEST_CHANGES" else 0xFFA500)
                log(f"PR #{num} → {decision}")
        except Exception as ex:
            log(f"PR #{num} parse err: {ex}", "WARN")
        time.sleep(2)

def generate_changelog(last_tag, tasks_done):
    compare = gh_compare(last_tag, "HEAD")
    commits = compare.get("commits",[])
    groups  = {"kernel":[],"driver":[],"feat":[],"fix":[],"other":[]}
    for commit in commits[:30]:
        msg = commit.get("commit",{}).get("message","").split("\n")[0]
        sha = commit.get("sha","")[:7]
        if not msg: continue
        entry = f"- `{sha}` {msg[:80]}"
        if   msg.startswith("kernel:"): groups["kernel"].append(entry)
        elif msg.startswith("driver:"): groups["driver"].append(entry)
        elif msg.startswith("feat"):    groups["feat"].append(entry)
        elif msg.startswith("fix:"):    groups["fix"].append(entry)
        else:                           groups["other"].append(entry)
    labels = {"kernel":"🔧 Kernel","driver":"💾 Drivers","feat":"✨ Features",
              "fix":"🐛 Fixes","other":"📝 Autres"}
    out = ""
    for key, entries in groups.items():
        if entries:
            out += f"### {labels[key]}\n" + "\n".join(entries) + "\n\n"
    if not out:
        out = "\n".join(f"- {t.get('nom','?')[:60]}" for t in tasks_done)
    return out

def create_release(tasks_done, tasks_failed, analyse, stats):
    releases = gh_list_releases(5)
    last_tag = "v0.0.0"
    for r in releases:
        tag = r.get("tag_name","")
        if re.match(r"v\d+\.\d+\.\d+", tag):
            last_tag = tag; break
    try:
        parts = last_tag.lstrip("v").split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    except: major, minor, patch = 0,0,0
    score = analyse.get("score_actuel", 30)
    if score >= 70: minor += 1; patch = 0
    else: patch += 1
    new_tag = f"v{major}.{minor}.{patch}"
    niveau  = analyse.get("niveau_os","?")
    ms      = analyse.get("prochaine_milestone","?")
    feats   = analyse.get("fonctionnalites_presentes",[])

    feat_txt = "\n".join(f"- ✅ {f}" for f in feats[:8]) or "- (Aucune)"

    changes_txt = ""
    for t in tasks_done:
        nom   = t.get("nom","?")[:60]
        sha   = t.get("sha","?")
        model = t.get("model","?")
        fx    = f" (après {t.get('fix_count',0)} fix)" if t.get("fix_count",0) > 0 else ""
        changes_txt += f"- ✅ {nom} [`{sha}`] ({model}){fx}\n"
    changes_txt = changes_txt or "- Maintenance\n"

    failed_txt = ""
    if tasks_failed:
        failed_txt = "\n## ⏭️ Reporté\n\n" + "\n".join(f"- ❌ {n}" for n in tasks_failed) + "\n"

    total_elapsed = round(time.time() - START_TIME, 0)
    total_tokens  = sum(KEY_STATE["tokens"].values())
    total_calls   = sum(KEY_STATE["usage"].values())
    models_used   = ", ".join(sorted(set(
        ACTIVE_MODELS.get(i,{}).get("model","?")
        for i in range(len(API_KEYS)) if i in ACTIVE_MODELS
    )))
    changelog = generate_changelog(last_tag, tasks_done)
    now       = datetime.utcnow()

    body = (
        f"# MaxOS {new_tag}\n\n"
        f"> 🤖 MaxOS AI Developer v{VERSION}\n\n"
        f"---\n\n## 📊 État\n\n"
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
        f"---\n\n## 🚀 Tester MaxOS\n\n"
        f"```bash\nsudo apt install qemu-system-x86\n"
        f"qemu-system-i386 -drive format=raw,file=os.img,if=floppy "
        f"-boot a -vga std -k fr -m 32 -no-reboot\n```\n\n"
        f"## ⚙️ Technique\n\n"
        f"| | |\n|---|---|\n"
        f"| Arch | x86 32-bit Protected Mode |\n"
        f"| CC | GCC -m32 -ffreestanding -nostdlib |\n"
        f"| ASM | NASM ELF32 |\n"
        f"| IA | {models_used} |\n"
        f"| Appels | {total_calls} |\n"
        f"| ~Tokens | {total_tokens} |\n"
        f"| Durée | {int(total_elapsed)}s |\n\n"
        f"---\n*MaxOS AI v{VERSION} | {now.strftime('%Y-%m-%d %H:%M')} UTC*\n"
    )

    url = gh_create_release(
        new_tag,
        f"MaxOS {new_tag} | {niveau} | {now.strftime('%Y-%m-%d')}",
        body,
        pre=(score < 50)
    )
    if url:
        disc_send_simple("🚀 Release créée",
                         f"**{new_tag}** — Score: {score}/100 | {niveau}",
                         0x00FF88,
                         [{"name":"Version","value":new_tag,"inline":True},
                          {"name":"Score","value":f"{score}/100","inline":True},
                          {"name":"Lien","value":f"[Release]({url})","inline":False}])
        log(f"Release {new_tag} → {url}")
    return url

def final_report(success, total, tasks_done, tasks_failed, analyse, stats):
    score  = analyse.get("score_actuel",30)
    niveau = analyse.get("niveau_os","?")
    pct    = int(success/total*100) if total > 0 else 0
    color  = 0x00FF88 if pct >= 80 else 0xFFA500 if pct >= 50 else 0xFF4444

    total_elapsed = round(time.time()-START_TIME, 0)
    total_tokens  = sum(KEY_STATE["tokens"].values())
    total_calls   = sum(KEY_STATE["usage"].values())
    total_errors  = sum(KEY_STATE["errors"].values())

    sources = read_all()
    quality = analyze_quality(sources)

    done_str = "\n".join(
        f"✅ {t.get('nom','?')[:40]} ({t.get('elapsed',0):.0f}s)"
        for t in tasks_done
    ) or "Aucune"
    fail_str = "\n".join(f"❌ {n[:40]}" for n in tasks_failed) or "Aucune"

    disc_send_simple(
        f"🏁 Cycle terminé — {success}/{total} tâches réussies",
        f"```\n{pbar(pct)}\n```",
        color,
        [{"name":"✅ Succès",       "value":str(success),               "inline":True},
         {"name":"❌ Échecs",        "value":str(total-success),         "inline":True},
         {"name":"📈 Taux",          "value":f"{pct}%",                  "inline":True},
         {"name":"⏱️ Durée",         "value":f"{int(total_elapsed)}s",   "inline":True},
         {"name":"🔑 Appels",        "value":str(total_calls),           "inline":True},
         {"name":"💬 ~Tokens",       "value":str(total_tokens),          "inline":True},
         {"name":"🚨 Erreurs API",   "value":str(total_errors),          "inline":True},
         {"name":"📊 Score qualité", "value":f"{quality['score']}/100",  "inline":True},
         {"name":"📁 Fichiers",      "value":str(stats.get("files",0)),  "inline":True},
         {"name":"📝 Lignes",        "value":str(stats.get("lines",0)),  "inline":True},
         {"name":"📊 Score OS",      "value":f"{score}/100 — {niveau}",  "inline":False},
         {"name":"✅ Réussies",      "value":done_str[:900],             "inline":False},
         {"name":"❌ Échouées",      "value":fail_str[:400],             "inline":False},
         {"name":"🔑 État clés",     "value":key_status_str(),           "inline":False}]
    )
    if quality["violations"]:
        viols = "\n".join(f"• `{v}`" for v in quality["violations"][:10])
        disc_send_simple("⚠️ Violations bare metal",
                         f"```\n{viols}\n```", 0xFF6600)

def cleanup_artifacts():
    build_dir = os.path.join(REPO_PATH,"build")
    if not os.path.exists(build_dir): return
    cleaned = 0
    for fname in os.listdir(build_dir):
        if fname.endswith((".o",".img.old")):
            try: os.remove(os.path.join(build_dir,fname)); cleaned += 1
            except: pass
    if cleaned: log(f"Cleanup: {cleaned} artefact(s) supprimé(s)")

def main():
    print("="*60)
    print(f"  MaxOS AI Developer v{VERSION}")
    print(f"  Batch mode | Anti-429 | Heartbeat Discord")
    print("="*60+"\n")

    if not init_models():
        print("FATAL: Aucune clé Gemini opérationnelle")
        sys.exit(1)

    disc_send_simple(
        f"🤖 MaxOS AI v{VERSION} démarré",
        f"`{len(ACTIVE_MODELS)}/{len(API_KEYS)}` clés actives",
        0x5865F2,
        [{"name":"Modèles","value":key_status_str(),"inline":False},
         {"name":"Repo","value":f"{REPO_OWNER}/{REPO_NAME}","inline":True},
         {"name":"Mode","value":"Batch anti-429","inline":True},
         {"name":"Heartbeat","value":f"Toutes {DISC_LOG_INTERVAL}s","inline":True}]
    )

    cleanup_artifacts()

    log("Setup labels...")
    created = gh_ensure_labels(STANDARD_LABELS)
    if created > 0:
        disc_log(f"🏷️ {created} label(s) créé(s)", key_status_str(), 0x5865F2)

    log("Traitement des issues...")
    handle_issues()
    if not watchdog(): sys.exit(0)

    log("Stale bot...")
    handle_stale_issues()

    log("Traitement des PRs...")
    handle_prs()
    if not watchdog(): sys.exit(0)

    sources = read_all(force=True)
    stats   = proj_stats(sources)
    quality = analyze_quality(sources)
    log(f"Sources: {stats['files']} fichiers, {stats['lines']} lignes")
    log(f"Qualité: {quality['score']}/100 | {quality.get('c_files',0)} .c | {quality.get('asm_files',0)} .asm")

    disc_send_simple(
        "📊 Sources analysées",
        f"`{stats['files']}` fichiers | `{stats['lines']}` lignes | `{stats['chars']}` chars",
        0x5865F2,
        [{"name":"📋 Qualité","value":f"{quality['score']}/100 ({len(quality['violations'])} violations)","inline":True},
         {"name":"📁 C files","value":str(quality.get("c_files",0)),"inline":True},
         {"name":"📁 ASM files","value":str(quality.get("asm_files",0)),"inline":True}]
    )

    if quality["violations"]:
        for v in quality["violations"][:5]:
            log(f"  Violation: {v}", "WARN")

    print("\n"+"="*60+"\n PHASE 1: Analyse\n"+"="*60)
    analyse = batch_analyse_and_plan(sources, stats)

    score      = analyse.get("score_actuel",30)
    niveau     = analyse.get("niveau_os","?")
    plan       = analyse.get("plan_ameliorations",[])
    milestone  = analyse.get("prochaine_milestone","?")
    features   = analyse.get("fonctionnalites_presentes",[])
    manquantes = analyse.get("fonctionnalites_manquantes_critiques",[])

    order = {"CRITIQUE":0,"HAUTE":1,"NORMALE":2,"BASSE":3}
    plan  = sorted(plan, key=lambda t: order.get(t.get("priorite","NORMALE"),2))

    log(f"Analyse: score={score} | {niveau} | {len(plan)} tâches | {milestone}")

    if milestone and milestone != "?":
        ms_num = gh_ensure_milestone(milestone)
        if ms_num: log(f"Milestone '{milestone}' = #{ms_num}")

    disc_send_simple(
        f"📊 Score {score}/100 — {niveau}",
        f"```\n{pbar(score)}\n```",
        0x00AAFF if score>=60 else 0xFFA500 if score>=30 else 0xFF4444,
        [{"name":"✅ Présentes",
          "value":"\n".join(f"+ {f}" for f in features[:6]) or "?","inline":True},
         {"name":"❌ Manquantes",
          "value":"\n".join(f"- {f}" for f in manquantes[:6]) or "?","inline":True},
         {"name":"📋 Plan",
          "value":"\n".join(
              f"[{i+1}] `{t.get('priorite','?')}` {t.get('nom','?')[:35]}"
              for i,t in enumerate(plan[:6])
          ),"inline":False},
         {"name":"🎯 Milestone","value":milestone[:80],"inline":True},
         {"name":"🔑 Clés","value":key_status_str(),"inline":False}]
    )

    print("\n"+"="*60+"\n PHASE 2: Implémentation\n"+"="*60)

    total        = len(plan)
    success      = 0
    tasks_done   = []
    tasks_failed = []

    for i, task in enumerate(plan, 1):
        if not watchdog(): break

        disc_send_heartbeat(i, total,
                            f"Prochaine tâche: **{task.get('nom','?')[:50]}** | "
                            f"Score actuel: `{score}/100`")

        sources_fresh = read_all()
        ok, written, deleted, metrics = phase_implement_one(task, sources_fresh, i, total)
        TASK_METRICS.append(metrics)

        if ok:
            success += 1
            tasks_done.append(metrics)
        else:
            tasks_failed.append(task.get("nom","?"))

        if i < total:
            n_ok = sum(1 for ii in range(len(API_KEYS))
                       if API_KEYS[ii] and time.time() >= KEY_STATE["cooldowns"].get(ii,0))
            pause = 8 if n_ok >= 2 else 15
            log(f"Pause {pause}s entre tâches...")
            flush_disc_log(force=True)
            time.sleep(pause)

    if success > 0:
        log("Création de la release...")
        sources_final = read_all(force=True)
        stats_final   = proj_stats(sources_final)
        create_release(tasks_done, tasks_failed, analyse, stats_final)

    sources_final = read_all(force=True)
    stats_final   = proj_stats(sources_final)
    final_report(success, total, tasks_done, tasks_failed, analyse, stats_final)

    flush_disc_log(force=True)

    print("\n"+"="*60)
    print(f"[FIN] {success}/{total} tâches | Uptime: {uptime()} | RL: {GH_RATE['remaining']}")
    if tasks_done:
        print("✅ Succès:")
        for t in tasks_done:
            print(f"  - {t.get('nom','?')[:60]} ({t.get('elapsed',0):.0f}s)")
    if tasks_failed:
        print("❌ Échecs:")
        for n in tasks_failed:
            print(f"  - {n[:60]}")

if __name__ == "__main__":
    main()
