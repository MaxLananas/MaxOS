#!/usr/bin/env python3
"""MaxOS AI Developer v9.1 - Basé sur v8.1 qui fonctionnait"""

import os, sys, json, time, subprocess, re
import urllib.request, urllib.error
from datetime import datetime

# ══════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════
def load_api_keys():
    keys = []
    k1 = os.environ.get("GEMINI_API_KEY", "")
    if k1: keys.append(k1)
    for i in range(2, 10):
        k = os.environ.get("GEMINI_API_KEY_" + str(i), "")
        if k: keys.append(k)
    return keys

API_KEYS        = load_api_keys()
GITHUB_TOKEN    = os.environ.get("GH_PAT", "") or os.environ.get("GITHUB_TOKEN", "")
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")
REPO_OWNER      = os.environ.get("REPO_OWNER", "MaxLananas")
REPO_NAME       = os.environ.get("REPO_NAME", "MaxOS")
REPO_PATH       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def mask_key(k):
    return k[:4] + "*" * max(0, len(k)-8) + k[-4:] if len(k) > 8 else "***"

print("[v9.1] " + str(len(API_KEYS)) + " cle(s) Gemini")
for i, k in enumerate(API_KEYS):
    print("  Cle " + str(i+1) + ": " + mask_key(k))
print("[v9.1] Discord: " + ("OK" if DISCORD_WEBHOOK else "ABSENT"))
print("[v9.1] GitHub:  " + ("OK" if GITHUB_TOKEN else "NON"))
print("[v9.1] Repo:    " + REPO_OWNER + "/" + REPO_NAME)

if not API_KEYS:
    print("FATAL: GEMINI_API_KEY manquante")
    sys.exit(1)

# ══════════════════════════════════════════════════════
# MODÈLES - gemini-2.5-flash EN PREMIER (le plus fiable)
# ══════════════════════════════════════════════════════
MODELS_PRIORITY = [
    "gemini-2.5-flash",         # Meilleur rapport qualité/vitesse
    "gemini-2.5-flash-lite",    # Fallback rapide
    "gemini-2.0-flash",         # Fallback secondaire
    "gemini-1.5-flash-latest",  # Dernier recours
]

# ══════════════════════════════════════════════════════
# ÉTAT GLOBAL
# ══════════════════════════════════════════════════════
KEY_STATE = {
    "current_index": 0,
    "cooldowns":     {},   # idx -> timestamp fin cooldown
    "usage_count":   {},   # idx -> nb appels
    "errors":        {},   # idx -> nb erreurs
    "forbidden":     {},   # idx -> set(modeles interdits)
}
ACTIVE_MODELS = {}  # idx -> {"model": str, "url": str}

# ══════════════════════════════════════════════════════
# FICHIERS DU PROJET
# ══════════════════════════════════════════════════════
ALL_FILES = [
    "boot/boot.asm", "kernel/kernel_entry.asm", "kernel/kernel.c",
    "drivers/screen.h", "drivers/screen.c",
    "drivers/keyboard.h", "drivers/keyboard.c",
    "ui/ui.h", "ui/ui.c",
    "apps/notepad.h", "apps/notepad.c",
    "apps/terminal.h", "apps/terminal.c",
    "apps/sysinfo.h", "apps/sysinfo.c",
    "apps/about.h", "apps/about.c",
    "Makefile", "linker.ld",
]

# ══════════════════════════════════════════════════════
# MISSION ET RÈGLES
# ══════════════════════════════════════════════════════
OS_MISSION = """MISSION MAXOS - OBJECTIF OS COMPLET TYPE WINDOWS 11
L'IA est developpeur principal autonome 24h/24.
L'IA PEUT: creer, modifier, supprimer n'importe quel fichier.

PRIORITES:
1. IDT 256 entrees + PIC 8259 (IRQ remappes)
2. Timer PIT 8253 100Hz + sleep_ms + uptime
3. Memoire physique bitmap 4KB
4. Mode graphique VGA mode 13h (320x200)
5. Terminal 20+ commandes + historique
6. Systeme fichiers FAT12
7. GUI fenetres + souris
8. Reseau TCP/IP"""

BARE_METAL_RULES = """REGLES BARE METAL x86 ABSOLUES:
ZERO: #include <stddef.h|string.h|stdlib.h|stdio.h|stdint.h|stdbool.h>
ZERO: size_t NULL bool true false uint32_t malloc memset strlen printf
REMPLACER: size_t->unsigned int, NULL->0, bool->int, true->1, false->0
COMPILER: gcc -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie
ASM: nasm -f elf (.o) ou nasm -f bin (boot.bin)
LD: ld -m elf_i386 -T linker.ld --oformat binary
Nouveaux .c -> OBLIGATOIRE dans Makefile
SIGNATURES: nb_init() nb_draw() nb_key(char k)
            tm_init() tm_draw() tm_key(char k)
            si_draw() ab_draw()
            kb_init() kb_haskey() kb_getchar()
            v_init() v_put() v_str() v_fill()"""

# ══════════════════════════════════════════════════════
# ROTATION DES CLÉS
# ══════════════════════════════════════════════════════
def get_best_key():
    """Sélectionne la clé disponible. Attend si toutes en cooldown."""
    now = time.time()
    n = len(API_KEYS)

    for delta in range(n):
        idx = (KEY_STATE["current_index"] + delta) % n
        if API_KEYS[idx] and now >= KEY_STATE["cooldowns"].get(idx, 0):
            KEY_STATE["current_index"] = idx
            KEY_STATE["usage_count"][idx] = KEY_STATE["usage_count"].get(idx, 0) + 1
            return idx

    # Toutes en cooldown: attendre la moins longue
    valid = [i for i in range(n) if API_KEYS[i]]
    if not valid:
        print("FATAL: Aucune cle valide")
        sys.exit(1)
    best = min(valid, key=lambda i: KEY_STATE["cooldowns"].get(i, 0))
    wait = KEY_STATE["cooldowns"].get(best, 0) - now + 1
    print("[Keys] Toutes en cooldown. Attente " + str(int(wait)) + "s...")
    time.sleep(max(wait, 1))
    KEY_STATE["current_index"] = best
    return best

def set_cooldown(idx, secs):
    KEY_STATE["cooldowns"][idx] = time.time() + secs
    KEY_STATE["errors"][idx] = KEY_STATE["errors"].get(idx, 0) + 1
    n = len(API_KEYS)
    if n > 1:
        nxt = (idx + 1) % n
        for _ in range(n):
            if API_KEYS[nxt]: break
            nxt = (nxt + 1) % n
        KEY_STATE["current_index"] = nxt
        print("[Keys] Cle " + str(idx+1) + " cooldown " +
              str(secs) + "s -> cle " + str(nxt+1))
    else:
        print("[Keys] Cle 1 cooldown " + str(secs) + "s")

def key_status():
    now = time.time()
    lines = []
    for i in range(len(API_KEYS)):
        if not API_KEYS[i]: continue
        cd  = KEY_STATE["cooldowns"].get(i, 0)
        st  = "OK" if now >= cd else "CD+" + str(int(cd-now)) + "s"
        m   = ACTIVE_MODELS.get(i, {}).get("model", "?")
        c   = KEY_STATE["usage_count"].get(i, 0)
        lines.append("Cle " + str(i+1) + ": " + st +
                     " | " + str(c) + " appels | " + m)
    return "\n".join(lines) or "Aucune cle"

# ══════════════════════════════════════════════════════
# INIT MODÈLES (avec appels de test courts)
# ══════════════════════════════════════════════════════
def find_model_for_key(idx):
    """Trouve le meilleur modèle pour une clé. Test rapide."""
    if idx >= len(API_KEYS) or not API_KEYS[idx]:
        return False

    key      = API_KEYS[idx]
    forbidden = KEY_STATE["forbidden"].get(idx, set())

    for model in MODELS_PRIORITY:
        if model in forbidden:
            continue

        url = ("https://generativelanguage.googleapis.com/v1beta/models/" +
               model + ":generateContent?key=" + key)

        # Test minimaliste et rapide
        payload = json.dumps({
            "contents": [{"parts": [{"text": "Reply: OK"}]}],
            "generationConfig": {"maxOutputTokens": 5, "temperature": 0.0}
        }).encode()

        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read())
                text = extract_text(data)
                if text is not None:
                    print("[Init] Cle " + str(idx+1) + " -> " + model + " OK")
                    ACTIVE_MODELS[idx] = {"model": model, "url": url}
                    return True
                else:
                    print("[Init] Cle " + str(idx+1) + " " + model + " vide")

        except urllib.error.HTTPError as e:
            if e.code == 403:
                forbidden.add(model)
                KEY_STATE["forbidden"][idx] = forbidden
                print("[Init] Cle " + str(idx+1) + " " + model + " interdit (403)")
            elif e.code == 429:
                print("[Init] Cle " + str(idx+1) + " " + model + " rate limit")
                time.sleep(3)
            elif e.code == 404:
                forbidden.add(model)
                KEY_STATE["forbidden"][idx] = forbidden
            else:
                print("[Init] Cle " + str(idx+1) + " " + model +
                      " HTTP " + str(e.code))
            time.sleep(0.5)

        except Exception as ex:
            print("[Init] Cle " + str(idx+1) + " " + model + ": " + str(ex))
            time.sleep(0.5)

    print("[Init] Cle " + str(idx+1) + ": aucun modele disponible")
    return False

def find_all_models():
    print("[Init] Initialisation des cles...")
    ok = 0
    for i in range(len(API_KEYS)):
        if API_KEYS[i]:
            if find_model_for_key(i):
                ok += 1
            time.sleep(1)  # Éviter le rate limit entre tests
    print("[Init] " + str(ok) + "/" + str(len(API_KEYS)) + " cle(s) OK")
    return ok > 0

# ══════════════════════════════════════════════════════
# EXTRACTION TEXTE GEMINI (gère les thinking models)
# ══════════════════════════════════════════════════════
def extract_text(data):
    """Extrait le texte d'une réponse Gemini. Gère tous les cas."""
    try:
        cands = data.get("candidates", [])
        if not cands:
            return None

        c      = cands[0]
        finish = c.get("finishReason", "STOP")

        if finish in ("SAFETY", "RECITATION"):
            print("[Gemini] Bloque: " + finish)
            return None

        parts = c.get("content", {}).get("parts", [])
        if not parts:
            # Certains modèles mettent le texte directement dans content
            t = c.get("content", {}).get("text", "")
            return t if t else None

        texts = []
        for p in parts:
            if isinstance(p, dict) and not p.get("thought"):
                t = p.get("text", "")
                if t: texts.append(t)

        result = "".join(texts)
        return result if result else None

    except Exception as e:
        print("[Extract] Erreur: " + str(e))
        return None

# ══════════════════════════════════════════════════════
# APPEL GEMINI - TIMEOUT INTELLIGENT + ROTATION
# ══════════════════════════════════════════════════════
def gemini(prompt, max_tokens=32768, timeout=90):
    """
    Appel Gemini optimisé:
    - timeout=90s (pas 180s) pour éviter le blocage
    - 6 tentatives max (pas 24 minutes)
    - Rotation immédiate sur 429
    - Changement de modèle sur 403
    """
    if not ACTIVE_MODELS:
        if not find_all_models():
            return None

    if len(prompt) > 50000:
        prompt = prompt[:50000] + "\n[TRONQUE]"

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.05,
        }
    }).encode("utf-8")

    max_attempts = len(API_KEYS) * 3  # 3 tentatives par clé max

    for attempt in range(1, max_attempts + 1):
        idx = get_best_key()

        if idx not in ACTIVE_MODELS:
            if not find_model_for_key(idx):
                set_cooldown(idx, 120)
                continue

        model_info = ACTIVE_MODELS[idx]
        key        = API_KEYS[idx]
        url        = model_info["url"].split("?")[0] + "?key=" + key

        print("[Gemini] Cle " + str(idx+1) + "/" +
              model_info["model"] + " attempt=" + str(attempt) +
              " timeout=" + str(timeout) + "s")

        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw  = r.read().decode("utf-8")
                data = json.loads(raw)

            elapsed = round(time.time() - t0, 1)
            text    = extract_text(data)

            if text is None:
                print("[Gemini] Reponse vide/bloquee en " + str(elapsed) + "s")
                # Changer de modèle pour cette clé
                forbidden = KEY_STATE["forbidden"].setdefault(idx, set())
                forbidden.add(model_info["model"])
                if idx in ACTIVE_MODELS:
                    del ACTIVE_MODELS[idx]
                find_model_for_key(idx)
                continue

            finish = ""
            try:
                finish = data["candidates"][0].get("finishReason", "STOP")
            except Exception:
                pass

            print("[Gemini] OK " + str(len(text)) + " chars en " +
                  str(elapsed) + "s (finish=" + finish + ")")
            return text

        except urllib.error.HTTPError as e:
            elapsed = round(time.time() - t0, 1)
            body    = ""
            try: body = e.read().decode()[:200]
            except: pass

            print("[Gemini] HTTP " + str(e.code) + " cle=" + str(idx+1) +
                  " en " + str(elapsed) + "s")

            if e.code == 429:
                errs = KEY_STATE["errors"].get(idx, 0)
                wait = min(30 * (errs + 1), 120)
                set_cooldown(idx, wait)
                # Si autre clé dispo, rotation immédiate sans sleep
                now = time.time()
                autre_dispo = any(
                    API_KEYS[i] and now >= KEY_STATE["cooldowns"].get(i, 0)
                    for i in range(len(API_KEYS)) if i != idx
                )
                if not autre_dispo:
                    sleep_time = min(wait, 45)
                    print("[Gemini] Attente " + str(sleep_time) + "s...")
                    time.sleep(sleep_time)

            elif e.code == 403:
                # Modèle interdit pour cette clé -> essayer le suivant
                forbidden = KEY_STATE["forbidden"].setdefault(idx, set())
                forbidden.add(model_info["model"])
                print("[Gemini] Modele " + model_info["model"] +
                      " interdit cle " + str(idx+1))
                if idx in ACTIVE_MODELS:
                    del ACTIVE_MODELS[idx]
                if not find_model_for_key(idx):
                    set_cooldown(idx, 600)

            elif e.code in (400, 404):
                if idx in ACTIVE_MODELS:
                    del ACTIVE_MODELS[idx]
                find_model_for_key(idx)

            elif e.code == 500:
                time.sleep(20)

            else:
                time.sleep(15)

        except TimeoutError:
            print("[Gemini] TIMEOUT " + str(timeout) + "s cle=" + str(idx+1))
            # Pas de cooldown sur timeout, juste changer de clé
            KEY_STATE["current_index"] = (idx + 1) % len(API_KEYS)

        except Exception as ex:
            print("[Gemini] Exception: " + str(ex))
            time.sleep(10)

    print("[Gemini] ECHEC apres " + str(max_attempts) + " tentatives")
    return None

# ══════════════════════════════════════════════════════
# DISCORD
# ══════════════════════════════════════════════════════
def discord_send(embeds):
    if not DISCORD_WEBHOOK:
        return False
    payload = json.dumps({
        "username": "MaxOS AI Bot",
        "embeds": embeds[:10]
    }).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WEBHOOK, data=payload,
        headers={"Content-Type": "application/json",
                 "User-Agent": "MaxOS-Bot/9.1"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status in (200, 204)
    except urllib.error.HTTPError as e:
        body = ""
        try: body = e.read().decode()[:200]
        except: pass
        print("[Discord] HTTP " + str(e.code) + ": " + body)
        if e.code == 401:
            print("[Discord] WEBHOOK INVALIDE!")
    except Exception as ex:
        print("[Discord] " + str(ex))
    return False

def make_embed(title, desc, color, fields=None):
    now = time.time()
    active = sum(1 for i in range(len(API_KEYS))
                 if API_KEYS[i] and now >= KEY_STATE["cooldowns"].get(i, 0))
    cur_model = ACTIVE_MODELS.get(
        KEY_STATE["current_index"], {}
    ).get("model", "?")
    e = {
        "title":       str(title)[:256],
        "description": str(desc)[:4096],
        "color":       color,
        "timestamp":   datetime.utcnow().isoformat() + "Z",
        "footer": {"text": (
            "MaxOS AI v9.1 | " + cur_model +
            " | " + str(active) + "/" + str(len(API_KEYS)) + " cles"
        )}
    }
    if fields:
        e["fields"] = [
            {"name": str(f.get("name",""))[:256],
             "value": str(f.get("value","?"))[:1024],
             "inline": bool(f.get("inline", False))}
            for f in fields[:25]
        ]
    return e

def d(title, desc="", color=0x5865F2, fields=None):
    discord_send([make_embed(title, desc, color, fields)])

def pbar(pct, w=28):
    f = int(w * pct / 100)
    return "[" + "X"*f + "-"*(w-f) + "] " + str(pct) + "%"

# ══════════════════════════════════════════════════════
# GITHUB API
# ══════════════════════════════════════════════════════
def github_api(method, endpoint, data=None):
    if not GITHUB_TOKEN:
        return None
    url = ("https://api.github.com/repos/" +
           REPO_OWNER + "/" + REPO_NAME + "/" + endpoint)
    payload = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        url, data=payload,
        headers={
            "Authorization":       "Bearer " + GITHUB_TOKEN,
            "Accept":              "application/vnd.github+json",
            "Content-Type":        "application/json",
            "User-Agent":          "MaxOS-AI-Bot/9.1",
            "X-GitHub-Api-Version":"2022-11-28",
        },
        method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        print("[GitHub] " + method + " " + endpoint + " HTTP " + str(e.code))
        return None
    except Exception as ex:
        print("[GitHub] " + str(ex))
        return None

def gh_create_release(tag, name, body, pre=False):
    r = github_api("POST", "releases", {
        "tag_name": tag, "name": name, "body": body,
        "draft": False, "prerelease": pre
    })
    return r.get("html_url") if r and "html_url" in r else None

def gh_open_prs():
    r = github_api("GET", "pulls?state=open&per_page=10")
    return r if isinstance(r, list) else []

def gh_merge(num, title):
    r = github_api("PUT", "pulls/" + str(num) + "/merge", {
        "commit_title": "merge: " + title + " [AI]",
        "merge_method": "squash"
    })
    return bool(r and r.get("merged"))

def gh_comment(num, body):
    github_api("POST", "issues/" + str(num) + "/comments", {"body": body})

def gh_close(num):
    github_api("PATCH", "pulls/" + str(num), {"state": "closed"})

# ══════════════════════════════════════════════════════
# SOURCES
# ══════════════════════════════════════════════════════
SKIP_DIRS  = {".git", "build", "__pycache__", ".github", "ai_dev"}
SKIP_FILES = {"screen.h.save"}
SRC_EXTS   = {".c", ".h", ".asm", ".ld"}

def discover_files():
    found = []
    for root, dirs, files in os.walk(REPO_PATH):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f in SKIP_FILES: continue
            ext = os.path.splitext(f)[1]
            if ext in SRC_EXTS or f == "Makefile":
                rel = os.path.relpath(
                    os.path.join(root, f), REPO_PATH
                ).replace("\\", "/")
                found.append(rel)
    return sorted(found)

def read_all():
    sources = {}
    for f in sorted(set(ALL_FILES + discover_files())):
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    sources[f] = fh.read()
            except:
                sources[f] = None
        else:
            sources[f] = None
    return sources

def build_context(sources, max_chars=42000):
    ctx = "=== CODE SOURCE MAXOS ===\n\nFICHIERS:\n"
    for f, c in sources.items():
        ctx += "  " + ("[OK] " if c else "[--] ") + f + "\n"
    ctx += "\n"
    used = len(ctx)

    # Priorité aux fichiers clés
    prio = [
        "kernel/kernel.c", "kernel/kernel_entry.asm",
        "Makefile", "linker.ld",
        "drivers/screen.h", "drivers/keyboard.h",
        "ui/ui.h", "ui/ui.c",
    ]
    done = set()

    for f in prio:
        c = sources.get(f, "")
        if not c: continue
        block = "=" * 50 + "\nFICHIER: " + f + "\n" + "=" * 50 + "\n" + c + "\n\n"
        if used + len(block) > max_chars: continue
        ctx += block; used += len(block); done.add(f)

    for f, c in sources.items():
        if f in done or not c: continue
        block = "=" * 50 + "\nFICHIER: " + f + "\n" + "=" * 50 + "\n" + c + "\n\n"
        if used + len(block) > max_chars:
            ctx += "[" + f + " tronque]\n"
            continue
        ctx += block; used += len(block)

    return ctx

def proj_stats(sources):
    files = sum(1 for c in sources.values() if c)
    lines = sum(c.count("\n") for c in sources.values() if c)
    return {"files": files, "lines": lines}

# ══════════════════════════════════════════════════════
# GIT ET BUILD
# ══════════════════════════════════════════════════════
def git_cmd(args):
    r = subprocess.run(
        ["git"] + args, cwd=REPO_PATH,
        capture_output=True, text=True, timeout=60
    )
    return r.returncode == 0, r.stdout, r.stderr

def git_push(task_name, files_written, description, model_used):
    if not files_written:
        return True, None, None

    dirs = set(f.split("/")[0] for f in files_written if "/" in f)
    pmap = {"kernel":"kernel","drivers":"driver","boot":"boot",
            "ui":"ui","apps":"feat(apps)","lib":"lib"}
    prefix = next((pmap[d] for d in pmap if d in dirs), "feat")

    fshort = ", ".join(os.path.basename(f) for f in files_written[:4])
    if len(files_written) > 4: fshort += " +" + str(len(files_written)-4)

    short = prefix + ": " + task_name[:50] + " [" + fshort + "]"
    body  = (
        "\n\nComponent : " + ", ".join(sorted(dirs)) + "\n"
        "Files     : " + ", ".join(files_written) + "\n"
        "Model     : " + model_used + "\n"
        "Timestamp : " + datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") + "\n"
        "\nDescription:\n  " + description[:200] + "\n"
        "\narch: x86-32 | gcc -m32 -ffreestanding | nasm ELF32"
    )

    git_cmd(["add", "-A"])
    ok, out, err = git_cmd(["commit", "-m", short + body])
    if not ok:
        if "nothing to commit" in (out + err):
            print("[Git] Rien a committer")
            return True, None, None
        print("[Git] Commit KO: " + err[:200])
        return False, None, None

    _, sha, _ = git_cmd(["rev-parse", "HEAD"])
    sha = sha.strip()[:7]

    ok2, _, e2 = git_cmd(["push"])
    if not ok2:
        # Retry avec rebase
        git_cmd(["pull", "--rebase"])
        ok2, _, e2 = git_cmd(["push"])
        if not ok2:
            print("[Git] Push KO: " + e2[:200])
            return False, None, None

    print("[Git] " + sha + ": " + short)
    return True, sha, short

def make_build():
    subprocess.run(["make", "clean"], cwd=REPO_PATH,
                   capture_output=True, timeout=30)
    r = subprocess.run(
        ["make"], cwd=REPO_PATH,
        capture_output=True, text=True, timeout=120
    )
    ok  = r.returncode == 0
    log = r.stdout + r.stderr
    errs = [l.strip() for l in log.split("\n") if "error:" in l.lower()][:15]
    print("[Build] " + ("OK" if ok else "ECHEC") +
          " (" + str(len(errs)) + " erreurs)")
    for e in errs[:5]: print("  >> " + e[:100])
    return ok, log, errs

# ══════════════════════════════════════════════════════
# PARSER
# ══════════════════════════════════════════════════════
def parse_files(response):
    files   = {}
    to_del  = []
    cur     = None
    lines   = []
    in_file = False

    for line in response.split("\n"):
        s = line.strip()

        if "=== FILE:" in s and s.endswith("==="):
            try:
                fname = s[s.index("=== FILE:")+9:s.rindex("===")].strip().strip("`").strip()
                if fname: cur = fname; lines = []; in_file = True
            except: pass
            continue

        if s == "=== END FILE ===" and in_file:
            if cur:
                content = "\n".join(lines).strip()
                for lang in ["```c","```asm","```nasm","```makefile","```ld","```bash","```"]:
                    if content.startswith(lang):
                        content = content[len(lang):].lstrip("\n"); break
                if content.endswith("```"):
                    content = content[:-3].rstrip("\n")
                if content.strip():
                    files[cur] = content.strip()
                    print("[Parse] " + cur + " (" + str(len(content)) + " chars)")
            cur = None; lines = []; in_file = False
            continue

        if "=== DELETE:" in s and s.endswith("==="):
            try:
                fname = s[s.index("=== DELETE:")+11:s.rindex("===")].strip()
                if fname: to_del.append(fname); print("[Parse] DEL: " + fname)
            except: pass
            continue

        if in_file: lines.append(line)

    return files, to_del

def write_files(files):
    written = []
    for path, content in files.items():
        if path.startswith("/") or ".." in path: continue
        full = os.path.join(REPO_PATH, path)
        os.makedirs(os.path.dirname(full) or REPO_PATH, exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        written.append(path)
        print("[Write] " + path)
    return written

def delete_files(paths):
    deleted = []
    for path in paths:
        if path.startswith("/") or ".." in path: continue
        full = os.path.join(REPO_PATH, path)
        if os.path.exists(full):
            os.remove(full)
            deleted.append(path)
            print("[Del] " + path)
    return deleted

def backup_files(paths):
    bak = {}
    for p in paths:
        full = os.path.join(REPO_PATH, p)
        if os.path.exists(full):
            with open(full, "r", encoding="utf-8", errors="ignore") as f:
                bak[p] = f.read()
    return bak

def restore_files(bak):
    for p, c in bak.items():
        full = os.path.join(REPO_PATH, p)
        os.makedirs(os.path.dirname(full) or REPO_PATH, exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as f:
            f.write(c)
    if bak: print("[Restore] " + str(len(bak)) + " fichier(s)")

# ══════════════════════════════════════════════════════
# PHASE 1: ANALYSE
# ══════════════════════════════════════════════════════
def phase_analyse(context, stats):
    print("\n[Phase 1] Analyse...")

    prompt = (
        "Tu es un expert OS bare metal x86.\n\n" +
        BARE_METAL_RULES + "\n\n" +
        OS_MISSION + "\n\n" +
        context + "\n\n"
        "STATS: " + str(stats["files"]) + " fichiers, " +
        str(stats["lines"]) + " lignes\n\n"
        "Retourne UNIQUEMENT ce JSON (commence par {, rien avant):\n\n"
        "{\n"
        '  "score_actuel": 35,\n'
        '  "niveau_os": "Prototype bare metal",\n'
        '  "fonctionnalites_presentes": ["Boot x86", "VGA texte"],\n'
        '  "fonctionnalites_manquantes_critiques": ["IDT", "Timer PIT"],\n'
        '  "plan_ameliorations": [\n'
        '    {\n'
        '      "nom": "IDT + PIC 8259",\n'
        '      "priorite": "CRITIQUE",\n'
        '      "categorie": "kernel",\n'
        '      "fichiers_a_modifier": ["kernel/kernel.c"],\n'
        '      "fichiers_a_creer": ["kernel/idt.h", "kernel/idt.c"],\n'
        '      "fichiers_a_supprimer": [],\n'
        '      "description": "Details techniques precis",\n'
        '      "impact_attendu": "Visible dans QEMU",\n'
        '      "complexite": "HAUTE"\n'
        '    }\n'
        '  ],\n'
        '  "prochaine_milestone": "Kernel stable"\n'
        "}"
    )

    resp = gemini(prompt, max_tokens=3500, timeout=60)
    if not resp:
        print("[Phase 1] Gemini KO -> plan par defaut")
        return default_plan()

    print("[Phase 1] " + str(len(resp)) + " chars")

    clean = resp.strip()
    if clean.startswith("```"):
        lines = clean.split("\n")[1:]
        if lines and lines[-1].strip() == "```": lines = lines[:-1]
        clean = "\n".join(lines).strip()

    clean = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', clean)

    for _ in range(3):
        i = clean.find("{")
        j = clean.rfind("}") + 1
        if i >= 0 and j > i:
            try:
                return json.loads(clean[i:j])
            except json.JSONDecodeError as e:
                print("[Phase 1] JSON err: " + str(e))
                clean = clean[i+1:]

    return default_plan()

def default_plan():
    return {
        "score_actuel": 30,
        "niveau_os": "Prototype bare metal",
        "fonctionnalites_presentes": [
            "Boot x86", "VGA texte", "Clavier PS/2", "4 apps"
        ],
        "fonctionnalites_manquantes_critiques": [
            "IDT", "Timer PIT", "Memoire", "Mode graphique", "FAT12"
        ],
        "prochaine_milestone": "Kernel stable IDT+Timer",
        "plan_ameliorations": [
            {
                "nom": "IDT 256 entrees + PIC 8259 + handlers",
                "priorite": "CRITIQUE", "categorie": "kernel",
                "fichiers_a_modifier": [
                    "kernel/kernel.c", "kernel/kernel_entry.asm", "Makefile"
                ],
                "fichiers_a_creer": ["kernel/idt.h", "kernel/idt.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "IDT 256 entrees. PIC 8259 remappage IRQ0-7->32-39. "
                    "Stubs NASM vecteurs 0-47. Handlers exceptions 0-31. "
                    "panic() ecran rouge. sti() a la fin de kernel_main."
                ),
                "impact_attendu": "OS stable, plus de triple fault",
                "complexite": "HAUTE"
            },
            {
                "nom": "Timer PIT 8253 100Hz + uptime + sleep_ms",
                "priorite": "CRITIQUE", "categorie": "kernel",
                "fichiers_a_modifier": ["kernel/kernel.c", "Makefile"],
                "fichiers_a_creer": ["kernel/timer.h", "kernel/timer.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "PIT canal 0 diviseur 11931=100Hz. "
                    "ticks volatile unsigned int. "
                    "timer_init() timer_ticks() sleep_ms(ms). "
                    "Uptime HH:MM:SS dans sysinfo."
                ),
                "impact_attendu": "Horloge systeme, uptime visible",
                "complexite": "MOYENNE"
            },
            {
                "nom": "Terminal 20 commandes + historique fleches",
                "priorite": "HAUTE", "categorie": "app",
                "fichiers_a_modifier": [
                    "apps/terminal.h", "apps/terminal.c"
                ],
                "fichiers_a_creer": [],
                "fichiers_a_supprimer": [],
                "description": (
                    "20 commandes: help ver mem uptime cls echo date "
                    "reboot halt color beep calc snake pong about "
                    "credits clear ps sysinfo license. "
                    "Historique 20 entrees fleche haut/bas."
                ),
                "impact_attendu": "Terminal complet type cmd.exe",
                "complexite": "MOYENNE"
            },
            {
                "nom": "Allocateur memoire bitmap pages 4KB",
                "priorite": "HAUTE", "categorie": "kernel",
                "fichiers_a_modifier": ["kernel/kernel.c", "Makefile"],
                "fichiers_a_creer": ["kernel/memory.h", "kernel/memory.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "Bitmap 1bit/page 4KB zone 1MB-16MB. "
                    "mem_init() mem_alloc() mem_free() "
                    "mem_used_kb() mem_total_kb(). Stats dans sysinfo."
                ),
                "impact_attendu": "Stats memoire dans sysinfo",
                "complexite": "HAUTE"
            },
            {
                "nom": "Mode VGA 320x200 256 couleurs + desktop",
                "priorite": "NORMALE", "categorie": "driver",
                "fichiers_a_modifier": [
                    "drivers/screen.h", "drivers/screen.c",
                    "kernel/kernel.c", "Makefile"
                ],
                "fichiers_a_creer": ["drivers/vga.h", "drivers/vga.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "Mode 13h 320x200 0xA0000. "
                    "vga_init() vga_pixel(x,y,c) vga_rect() vga_clear(). "
                    "Desktop degrade + taskbar. "
                    "Fallback mode texte si echec."
                ),
                "impact_attendu": "Interface graphique coloree",
                "complexite": "HAUTE"
            },
        ]
    }

# ══════════════════════════════════════════════════════
# PHASE 2: IMPLÉMENTATION
# ══════════════════════════════════════════════════════
def phase_implement(task, all_sources):
    nom       = task.get("nom", "?")
    categorie = task.get("categorie", "general")
    f_mod     = task.get("fichiers_a_modifier", [])
    f_new     = task.get("fichiers_a_creer", [])
    f_del     = task.get("fichiers_a_supprimer", [])
    desc      = task.get("description", "")
    impact    = task.get("impact_attendu", "")
    cx        = task.get("complexite", "MOYENNE")
    targets   = list(set(f_mod + f_new))

    model = ACTIVE_MODELS.get(KEY_STATE["current_index"], {}).get("model", "?")

    print("\n[Impl] " + nom)
    print("  Cat=" + categorie + " Cx=" + cx)
    print("  Mod=" + str(f_mod))
    print("  New=" + str(f_new))

    # Contexte ciblé: fichiers à toucher + dépendances
    needed = set(targets)
    for f in targets:
        partner = f.replace(".c", ".h") if f.endswith(".c") else f.replace(".h", ".c")
        if partner in all_sources: needed.add(partner)

    # Toujours inclure les fichiers essentiels
    for ess in ["kernel/kernel.c", "kernel/kernel_entry.asm",
                "drivers/screen.h", "drivers/keyboard.h",
                "ui/ui.h", "Makefile", "linker.ld"]:
        needed.add(ess)

    ctx = "=== FICHIERS CONCERNES ===\n\n"
    total_len = 0
    for f in sorted(needed):
        c = all_sources.get(f, "")
        block = "--- " + f + " ---\n" + (c if c else "[A CREER]") + "\n\n"
        if total_len + len(block) > 20000:
            ctx += "[" + f + " - trop grand, tronque]\n"
            continue
        ctx += block
        total_len += len(block)

    # Tokens selon complexité
    tok = {"HAUTE": 32768, "MOYENNE": 20480, "BASSE": 12288}
    max_tok = tok.get(cx, 20480)

    prompt = (
        "Tu es un expert OS bare metal x86.\n" +
        BARE_METAL_RULES + "\n\n" +
        OS_MISSION + "\n\n" +
        ctx + "\n"
        "TACHE: " + nom + "\n"
        "CATEGORIE: " + categorie + " | COMPLEXITE: " + cx + "\n"
        "DESCRIPTION: " + desc + "\n"
        "IMPACT: " + impact + "\n"
        "MODIFIER: " + str(f_mod) + "\n"
        "CREER: " + str(f_new) + "\n"
        "SUPPRIMER: " + str(f_del) + "\n\n"
        "INSTRUCTIONS:\n"
        "1. Code COMPLET - JAMAIS '// reste inchange' ou '...'\n"
        "2. Respecter TOUTES les regles bare metal\n"
        "3. Nouveaux .c -> ajouter dans Makefile\n"
        "4. Supprimer: === DELETE: chemin ===\n"
        "5. Tester mentalement que ca compile\n\n"
        "FORMAT OBLIGATOIRE:\n"
        "=== FILE: chemin/fichier.ext ===\n"
        "[code complet]\n"
        "=== END FILE ===\n\n"
        "COMMENCE:"
    )

    t0 = time.time()
    resp = gemini(prompt, max_tokens=max_tok, timeout=120)
    elapsed = round(time.time() - t0, 1)

    if not resp:
        d("❌ Echec: " + nom[:50],
          "Gemini n'a pas repondu apres " + str(elapsed) + "s",
          0xFF4444)
        return False, [], []

    print("[Impl] " + str(len(resp)) + " chars en " + str(elapsed) + "s")

    files, to_del = parse_files(resp)

    if not files and not to_del:
        print("[Debug] Debut reponse:\n" + resp[:400])
        d("⚠️ Parse vide: " + nom[:50],
          "Reponse reçue mais rien parse.", 0xFFA500)
        return False, [], []

    bak     = backup_files(list(files.keys()))
    written = write_files(files)
    deleted = delete_files(to_del)

    if not written and not deleted:
        return False, [], []

    ok, log, errs = make_build()

    if ok:
        pushed, sha, _ = git_push(nom, written + deleted, desc, model)
        if pushed:
            return True, written, deleted
        restore_files(bak)
        return False, [], []

    # Auto-fix si build KO
    fixed = auto_fix(log, errs, files, bak, model)
    if fixed:
        return True, written, deleted

    restore_files(bak)
    for p in written:
        if p not in bak:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp): os.remove(fp)
    return False, [], []

# ══════════════════════════════════════════════════════
# AUTO-FIX
# ══════════════════════════════════════════════════════
def auto_fix(log, errs, gen_files, bak, model, max_attempts=2):
    print("[Fix] " + str(len(errs)) + " erreurs...")

    for attempt in range(1, max_attempts + 1):
        print("[Fix] Tentative " + str(attempt) + "/" + str(max_attempts))

        curr = {}
        for p in gen_files:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp):
                with open(fp, "r") as f:
                    curr[p] = f.read()[:2500]

        ctx     = "".join("--- " + p + " ---\n" + c + "\n\n" for p, c in curr.items())
        err_str = "\n".join(errs[:10])

        prompt = (
            BARE_METAL_RULES + "\n\n"
            "ERREURS:\n```\n" + err_str + "\n```\n\n"
            "LOG (fin):\n```\n" + log[-1200:] + "\n```\n\n"
            "FICHIERS:\n" + ctx + "\n"
            "Corrige les erreurs. Code complet.\n\n"
            "=== FILE: fichier.ext ===\n[code]\n=== END FILE ==="
        )

        resp = gemini(prompt, max_tokens=24576, timeout=90)
        if not resp: continue

        files, _ = parse_files(resp)
        if not files: continue

        write_files(files)
        ok, log2, new_errs = make_build()

        if ok:
            git_push("fix: corrections compilation",
                     list(files.keys()),
                     "Auto-fix: " + str(len(errs)) + " erreurs -> 0",
                     model)
            d("🔧 Auto-fix OK",
              str(len(errs)) + " erreurs corrigees.", 0x00AAFF)
            return True

        errs = new_errs
        time.sleep(10)

    restore_files(bak)
    return False

# ══════════════════════════════════════════════════════
# PULL REQUESTS
# ══════════════════════════════════════════════════════
def handle_pull_requests():
    prs = gh_open_prs()
    if not prs:
        print("[PR] Aucune PR")
        return

    print("[PR] " + str(len(prs)) + " PR(s)")

    for pr in prs[:5]:
        num    = pr.get("number")
        title  = pr.get("title", "")
        author = pr.get("user", {}).get("login", "")

        if author in ("MaxOS-AI-Bot", "github-actions[bot]"):
            continue

        print("[PR] #" + str(num) + " par " + author)

        files_data = github_api("GET", "pulls/" + str(num) + "/files") or []
        flist = "\n".join("- " + f.get("filename","") for f in files_data[:10])

        prompt = (
            BARE_METAL_RULES + "\n\n"
            "PR #" + str(num) + " par " + author + "\n"
            "Titre: " + title + "\n"
            "Fichiers:\n" + flist + "\n\n"
            "JSON uniquement (commence par {):\n"
            '{"action":"MERGE","raison":"ok"}\n'
            "MERGE si bare metal OK. REJECT si libs standard."
        )

        resp = gemini(prompt, max_tokens=200, timeout=30)
        action = "REJECT"
        raison = "Analyse impossible"

        if resp:
            try:
                i = resp.find("{"); j = resp.rfind("}") + 1
                if i >= 0 and j > i:
                    dec    = json.loads(resp[i:j])
                    action = dec.get("action", "REJECT")
                    raison = dec.get("raison", "")
            except: pass

        gh_comment(num, "## 🤖 Review AI\n\n**" + action + "**\n\n" + raison)

        if action == "MERGE":
            if gh_merge(num, title):
                d("✅ PR #" + str(num) + " mergee", title, 0x00FF88)
            else:
                d("⚠️ PR #" + str(num) + " merge echoue", title, 0xFFA500)
        else:
            gh_close(num)
            d("❌ PR #" + str(num) + " rejetee", raison[:80], 0xFF4444)

# ══════════════════════════════════════════════════════
# RELEASE
# ══════════════════════════════════════════════════════
def create_release(tasks_done, tasks_failed, analyse_data, stats):
    if not GITHUB_TOKEN: return None

    r    = github_api("GET", "tags?per_page=1")
    last = r[0].get("name", "v0.0.0") if r and len(r) > 0 else "v0.0.0"

    try:
        parts = [int(x) for x in last.lstrip("v").split(".")]
        while len(parts) < 3: parts.append(0)
        if len(tasks_done) >= 3: parts[1] += 1; parts[2] = 0
        else: parts[2] += 1
        new_tag = "v" + ".".join(str(x) for x in parts)
    except:
        new_tag = "v1.0.0"

    score   = analyse_data.get("score_actuel", 30)
    niveau  = analyse_data.get("niveau_os", "Prototype")
    ms      = analyse_data.get("prochaine_milestone", "")
    feats   = analyse_data.get("fonctionnalites_presentes", [])
    now     = datetime.utcnow()

    models_used = ", ".join(sorted(set(
        ACTIVE_MODELS.get(i, {}).get("model", "")
        for i in range(len(API_KEYS)) if i in ACTIVE_MODELS
    )))

    changes = ""
    for t in tasks_done:
        sha  = t.get("sha", "")
        link = (" [`"+sha+"`](https://github.com/"+REPO_OWNER+"/"+REPO_NAME+
                "/commit/"+sha+")" if sha else "")
        changes += "- **" + t.get("nom","") + "**" + link + "\n"
        fs = t.get("files", [])
        if fs: changes += "  - `" + "`, `".join(fs[:4]) + "`\n"

    failed_txt = "".join("- ~~" + t + "~~\n" for t in tasks_failed)
    feat_txt   = "\n".join("  - " + f for f in feats)

    body = (
        "# MaxOS " + new_tag + "\n\n"
        "> 🤖 MaxOS AI Developer v9.1 - Objectif: Windows 11\n\n"
        "---\n\n## 📊 État\n\n"
        "| | |\n|---|---|\n"
        "| Score | **" + str(score) + "/100** |\n"
        "| Niveau | " + niveau + " |\n"
        "| Fichiers | " + str(stats.get("files",0)) + " |\n"
        "| Lignes | " + str(stats.get("lines",0)) + " |\n"
        "| Milestone | " + ms + " |\n\n"
        "## ✅ Changements\n\n" + (changes or "- Maintenance\n") +
        ("\n## ⏭️ Reporté\n\n" + failed_txt if failed_txt else "") +
        "\n## 🧩 Fonctionnalités\n\n" + feat_txt + "\n\n"
        "---\n\n## 🚀 Tester MaxOS\n\n"
        "### Linux/WSL\n```bash\n"
        "sudo apt install qemu-system-x86\n"
        "qemu-system-i386 -drive format=raw,file=os.img,if=floppy "
        "-boot a -vga std -k fr -m 32 -no-reboot\n```\n\n"
        "### Windows (QEMU)\n```\n"
        "qemu-system-i386.exe -drive format=raw,file=os.img,if=floppy "
        "-boot a -vga std -k fr -m 32\n```\n\n"
        "### Compiler\n```bash\n"
        "sudo apt install nasm gcc make gcc-multilib\n"
        "git clone https://github.com/" + REPO_OWNER + "/" + REPO_NAME + "\n"
        "cd " + REPO_NAME + " && make\n```\n\n"
        "## ⌨️ Contrôles\n\n"
        "| Touche | Action |\n|---|---|\n"
        "| TAB | Changer d'app |\n| F1 | Bloc-Notes |\n"
        "| F2 | Terminal |\n| F3 | Sysinfo |\n| F4 | A propos |\n\n"
        "## ⚙️ Technique\n\n"
        "| | |\n|---|---|\n"
        "| Arch | x86 32-bit Protected Mode |\n"
        "| CC | GCC -m32 -ffreestanding -nostdlib |\n"
        "| ASM | NASM ELF32 |\n"
        "| IA | " + models_used + " |\n\n"
        "---\n*MaxOS AI v9.1 | " + now.strftime("%Y-%m-%d %H:%M") + " UTC*\n"
    )

    url = gh_create_release(
        new_tag,
        "MaxOS " + new_tag + " | " + niveau + " | " + now.strftime("%Y-%m-%d"),
        body, pre=(score < 50)
    )

    if url:
        d("🚀 Release " + new_tag,
          "Score: " + str(score) + "/100 | " + niveau, 0x00FF88,
          [{"name":"Version",  "value": new_tag,            "inline": True},
           {"name":"Score",    "value": str(score)+"/100",  "inline": True},
           {"name":"Release",  "value": "[Voir]("+url+")",  "inline": False}])
        print("[Release] " + new_tag + " -> " + url)
    return url

# ══════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════
def main():
    print("=" * 55)
    print("  MaxOS AI Developer v9.1")
    print("  Basé sur v8.1 | gemini-2.5-flash en priorité")
    print("=" * 55 + "\n")

    if not find_all_models():
        print("FATAL: Aucune cle Gemini operationnelle")
        sys.exit(1)

    d("🤖 MaxOS AI v9.1 démarré",
      str(len(ACTIVE_MODELS)) + "/" + str(len(API_KEYS)) + " cles actives",
      0x5865F2,
      [{"name": "Modeles",
        "value": "\n".join(
            "Cle "+str(i+1)+": "+ACTIVE_MODELS[i]["model"]
            for i in sorted(ACTIVE_MODELS.keys())
        ) or "Aucun",
        "inline": False},
       {"name": "Repo", "value": REPO_OWNER+"/"+REPO_NAME, "inline": True}])

    # PRs
    print("\n[PRs] Check...")
    handle_pull_requests()

    # Sources
    sources = read_all()
    context = build_context(sources)
    stats   = proj_stats(sources)
    print("[Sources] "+str(stats["files"])+" fichiers, "+str(stats["lines"])+" lignes")

    # Phase 1: Analyse
    print("\n"+"="*55+"\n PHASE 1: Analyse\n"+"="*55)
    analyse = phase_analyse(context, stats)
    if not analyse:
        d("❌ Analyse echouee", "Impossible.", 0xFF0000)
        sys.exit(1)

    score     = analyse.get("score_actuel", 30)
    niveau    = analyse.get("niveau_os", "?")
    plan      = analyse.get("plan_ameliorations", [])
    milestone = analyse.get("prochaine_milestone", "?")
    features  = analyse.get("fonctionnalites_presentes", [])
    manquantes = analyse.get("fonctionnalites_manquantes_critiques", [])

    print("[Analyse] Score="+str(score)+" | "+niveau)
    print("[Analyse] "+str(len(plan))+" taches | "+milestone)

    order = {"CRITIQUE":0, "HAUTE":1, "NORMALE":2, "BASSE":3}
    plan  = sorted(plan, key=lambda t: order.get(t.get("priorite","NORMALE"), 2))

    d("📊 Score "+str(score)+"/100 - "+niveau,
      "```\n"+pbar(score)+"\n```",
      0x00AAFF if score>=60 else 0xFFA500 if score>=30 else 0xFF4444,
      [{"name": "✅ Presentes",
        "value": "\n".join("+ "+f for f in features[:5]) or "?",
        "inline": True},
       {"name": "❌ Manquantes",
        "value": "\n".join("- "+f for f in manquantes[:5]) or "?",
        "inline": True},
       {"name": "📋 Plan",
        "value": "\n".join(
            "["+str(i+1)+"] ["+t.get("priorite","?")+"] "+t.get("nom","?")[:40]
            for i,t in enumerate(plan[:6])
        ), "inline": False},
       {"name": "🎯 Milestone", "value": milestone[:80],  "inline": False},
       {"name": "🔑 Cles",      "value": key_status(),    "inline": False}])

    # Phase 2: Implémentation
    print("\n"+"="*55+"\n PHASE 2: Implementation\n"+"="*55)

    total        = len(plan)
    success      = 0
    tasks_done   = []
    tasks_failed = []

    for i, task in enumerate(plan, 1):
        nom      = task.get("nom", "Tache "+str(i))
        priorite = task.get("priorite", "NORMALE")
        cat      = task.get("categorie", "?")
        model    = ACTIVE_MODELS.get(KEY_STATE["current_index"],{}).get("model","?")

        print("\n"+"="*55)
        print("["+str(i)+"/"+str(total)+"] ["+priorite+"] "+nom)
        print("="*55)

        d("["+str(i)+"/"+str(total)+"] "+nom[:60],
          "```\n"+pbar(int((i-1)/total*100))+"\n```\n"+
          task.get("description","")[:150]+"...",
          0xFFA500,
          [{"name":"Priorite", "value": priorite, "inline": True},
           {"name":"Cat",      "value": cat,      "inline": True},
           {"name":"Modele",   "value": model,    "inline": True}])

        sources = read_all()
        ok, written, deleted = phase_implement(task, sources)

        _, sha_raw, _ = git_cmd(["rev-parse", "HEAD"])
        sha = sha_raw.strip()[:7] if sha_raw.strip() else "?"

        if ok:
            success += 1
            tasks_done.append({
                "nom": nom, "sha": sha,
                "files": written+deleted, "model": model
            })
            d("✅ Succès: "+nom[:50],
              "Commit `"+sha+"`", 0x00FF88,
              [{"name":"📝 Ecrits",
                "value": "\n".join("`"+f+"`" for f in written[:5]) or "Aucun",
                "inline": True},
               {"name":"🗑️ Supprimes",
                "value": "\n".join("`"+f+"`" for f in deleted) or "Aucun",
                "inline": True},
               {"name":"📊 Progress",
                "value": pbar(int(i/total*100)),
                "inline": False}])
            sources = read_all()
        else:
            tasks_failed.append(nom)
            d("❌ Echec: "+nom[:50], "Code restaure.", 0xFF6600)

        if i < total:
            n_ok = sum(1 for ii in range(len(API_KEYS))
                       if API_KEYS[ii] and
                       time.time() >= KEY_STATE["cooldowns"].get(ii,0))
            pause = 10 if n_ok >= 2 else 20
            print("[Pause] "+str(pause)+"s...")
            time.sleep(pause)

    # Release
    if success > 0:
        print("\n[Release] Creation...")
        sources = read_all()
        stats2  = proj_stats(sources)
        create_release(tasks_done, tasks_failed, analyse, stats2)

    pct   = int(success/total*100) if total > 0 else 0
    color = 0x00FF88 if pct>=80 else 0xFFA500 if pct>=50 else 0xFF4444

    d("🏁 Cycle fini - "+str(success)+"/"+str(total),
      "```\n"+pbar(pct)+"\n```", color,
      [{"name":"✅ Succes",  "value": str(success),        "inline": True},
       {"name":"❌ Echecs",  "value": str(total-success),  "inline": True},
       {"name":"📈 Taux",    "value": str(pct)+"%",        "inline": True},
       {"name":"🔑 Cles",    "value": key_status(),        "inline": False}])

    print("\n[FIN] "+str(success)+"/"+str(total))

if __name__ == "__main__":
    main()
