#!/usr/bin/env python3
"""MaxOS AI Developer v9.0 - Ultra-rapide, robuste, zéro timeout"""

import os, sys, json, time, subprocess, re, threading
import urllib.request, urllib.error
from datetime import datetime

# ══════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════
def load_keys():
    keys = []
    for var in ["GEMINI_API_KEY"] + ["GEMINI_API_KEY_"+str(i) for i in range(2,10)]:
        k = os.environ.get(var, "").strip()
        if k:
            keys.append(k)
    return keys

API_KEYS        = load_keys()
GITHUB_TOKEN    = os.environ.get("GITHUB_TOKEN", "")
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")
REPO_OWNER      = os.environ.get("REPO_OWNER", "MaxLananas")
REPO_NAME       = os.environ.get("REPO_NAME", "MaxOS")
REPO_PATH       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def mask(k):
    return k[:4] + "*"*max(0,len(k)-8) + k[-4:] if len(k)>8 else "***"

print("[v9.0] " + str(len(API_KEYS)) + " cle(s) Gemini")
for i,k in enumerate(API_KEYS):
    print("  Cle " + str(i+1) + ": " + mask(k))
print("[v9.0] Discord: " + ("OK" if DISCORD_WEBHOOK else "ABSENT"))
print("[v9.0] GitHub:  " + ("OK" if GITHUB_TOKEN else "NON"))
print("[v9.0] Repo:    " + REPO_OWNER + "/" + REPO_NAME)

if not API_KEYS:
    print("FATAL: GEMINI_API_KEY manquante")
    sys.exit(1)

# ══════════════════════════════════════════════════════
# MODELES - du plus rapide au plus puissant
# ══════════════════════════════════════════════════════
MODELS = [
    "gemini-2.0-flash",        # Rapide + fiable
    "gemini-2.5-flash",        # Bon équilibre
    "gemini-2.5-flash-lite",   # Quota élevé mais lent
    "gemini-1.5-flash",        # Fallback
    "gemini-1.5-flash-8b",     # Ultra-rapide, moins puissant
]

# ══════════════════════════════════════════════════════
# ÉTAT GLOBAL
# ══════════════════════════════════════════════════════
KS = {
    "current":   0,
    "cooldowns": {},   # idx -> timestamp fin cooldown
    "calls":     {},   # idx -> nb appels
    "errors":    {},   # idx -> nb erreurs
    "forbidden": {},   # idx -> set(modeles)
    "model":     {},   # idx -> modele actif
}

_lock = threading.Lock()

def get_model_url(idx):
    """Retourne l'URL du modèle actif pour une clé."""
    model = KS["model"].get(idx)
    if not model:
        return None, None
    key = API_KEYS[idx]
    url = ("https://generativelanguage.googleapis.com/v1beta/models/" +
           model + ":generateContent?key=" + key)
    return model, url

def assign_model(idx):
    """Assigne le meilleur modèle disponible à une clé."""
    forbidden = KS["forbidden"].get(idx, set())
    for m in MODELS:
        if m not in forbidden:
            KS["model"][idx] = m
            return m
    return None

def init_all():
    """Init rapide sans appels de test."""
    print("[Gemini] Init (sans appels test)...")
    ok = 0
    for i in range(len(API_KEYS)):
        if API_KEYS[i]:
            m = assign_model(i)
            if m:
                print("  Cle " + str(i+1) + " -> " + m)
                ok += 1
    print("[Gemini] " + str(ok) + "/" + str(len(API_KEYS)) + " cle(s) prete(s)")
    return ok > 0

def next_key():
    """Sélectionne la meilleure clé disponible."""
    now = time.time()
    n = len(API_KEYS)

    # Chercher une clé libre
    for delta in range(n):
        idx = (KS["current"] + delta) % n
        if not API_KEYS[idx]:
            continue
        if not KS["model"].get(idx):
            if not assign_model(idx):
                continue
        if now >= KS["cooldowns"].get(idx, 0):
            KS["current"] = idx
            KS["calls"][idx] = KS["calls"].get(idx, 0) + 1
            return idx

    # Toutes en cooldown: attendre la moins longue
    valid = [i for i in range(n) if API_KEYS[i] and KS["model"].get(i)]
    if not valid:
        print("[Keys] Aucune cle valide!")
        return 0
    best = min(valid, key=lambda i: KS["cooldowns"].get(i, 0))
    wait = KS["cooldowns"].get(best, 0) - now
    if wait > 0:
        print("[Keys] Attente " + str(int(wait)+1) + "s (toutes en cooldown)...")
        time.sleep(wait + 1)
    KS["current"] = best
    return best

def set_cooldown(idx, secs):
    KS["cooldowns"][idx] = time.time() + secs
    KS["errors"][idx] = KS["errors"].get(idx, 0) + 1
    n = len(API_KEYS)
    if n > 1:
        nxt = (idx + 1) % n
        KS["current"] = nxt
    print("[Keys] Cle " + str(idx+1) + " cooldown " + str(secs) + "s")

def keys_info():
    now = time.time()
    lines = []
    for i in range(len(API_KEYS)):
        if not API_KEYS[i]: continue
        cd = KS["cooldowns"].get(i, 0)
        st = "OK" if now >= cd else "CD+" + str(int(cd-now)) + "s"
        m  = KS["model"].get(i, "?")
        c  = KS["calls"].get(i, 0)
        lines.append("Cle " + str(i+1) + ": " + st +
                     " | " + str(c) + " calls | " + m)
    return "\n".join(lines) or "Aucune cle"

# ══════════════════════════════════════════════════════
# RÈGLES ET MISSION
# ══════════════════════════════════════════════════════
RULES = """=== REGLES BARE METAL x86 STRICTES ===
INTERDIT: #include <stddef.h|string.h|stdlib.h|stdio.h|stdint.h|stdbool.h>
INTERDIT: size_t NULL bool true false uint32_t uint8_t malloc memset strlen printf
REMPLACER: size_t->unsigned int, NULL->0, bool->int, true->1, false->0
COMPILER: gcc -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic
ASM: nasm -f elf (pour .o), nasm -f bin (pour boot.bin)
LD: ld -m elf_i386 -T linker.ld --oformat binary
Nouveaux .c -> OBLIGATOIRE les ajouter dans Makefile
SIGNATURES: nb_init() nb_draw() nb_key(char) | tm_init() tm_draw() tm_key(char)
            si_draw() ab_draw() | kb_init() kb_haskey() kb_getchar()
            v_init() v_put(x,y,c,attr) v_str(x,y,s,attr) v_fill(attr)"""

MISSION = """=== MISSION MAXOS ===
OS x86 complet évoluant vers Windows 11.
L'IA développe SEULE 24h/24: créer/modifier/supprimer tout fichier.
PRIORITÉS: IDT+PIC > Timer PIT > Mémoire > Graphique > Apps > FAT12 > Réseau"""

# ══════════════════════════════════════════════════════
# APPEL GEMINI - RAPIDE ET ROBUSTE
# ══════════════════════════════════════════════════════
def gemini(prompt, max_tokens=8192, timeout=90):
    """
    Appel Gemini optimisé:
    - Timeout court (90s) pour ne pas bloquer
    - Rotation immédiate sur erreur
    - Max 5 tentatives
    """
    if len(prompt) > 40000:
        prompt = prompt[:40000] + "\n[TRONQUE]"

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.15,
            "candidateCount": 1,
        }
    }).encode("utf-8")

    last_err = None
    for attempt in range(1, 6):
        idx = next_key()
        model, url = get_model_url(idx)

        if not url:
            if not assign_model(idx):
                set_cooldown(idx, 3600)
                continue
            model, url = get_model_url(idx)

        print("[Gemini] Cle " + str(idx+1) + "/" + model +
              " attempt=" + str(attempt) + " maxTok=" + str(max_tokens))

        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read().decode("utf-8")
                data = json.loads(raw)

            elapsed = round(time.time() - t0, 1)

            # Extraire texte
            cands = data.get("candidates", [])
            if not cands:
                fb = data.get("promptFeedback", {})
                reason = fb.get("blockReason", "UNKNOWN")
                print("[Gemini] Pas de candidat, block=" + reason)
                if reason in ("SAFETY", "OTHER"):
                    return None
                continue

            c = cands[0]
            finish = c.get("finishReason", "STOP")

            if finish in ("SAFETY", "RECITATION"):
                print("[Gemini] Bloque: " + finish)
                if finish == "RECITATION" and attempt <= 2:
                    prompt = "Ecris une implementation ORIGINALE:\n\n" + prompt[-3000:]
                    time.sleep(2)
                    continue
                return None

            parts = c.get("content", {}).get("parts", [])
            texts = [p["text"] for p in parts
                     if isinstance(p, dict) and p.get("text") and not p.get("thought")]
            text = "".join(texts).strip()

            if not text:
                print("[Gemini] Reponse vide (finish=" + finish + ")")
                if "MAX_TOKENS" in finish:
                    max_tokens = max(max_tokens // 2, 2048)
                    continue
                # Changer de modèle
                forbidden = KS["forbidden"].setdefault(idx, set())
                forbidden.add(model)
                KS["model"][idx] = ""
                assign_model(idx)
                continue

            print("[Gemini] OK " + str(len(text)) + " chars en " +
                  str(elapsed) + "s")
            return text

        except urllib.error.HTTPError as e:
            body = ""
            try: body = e.read().decode()[:300]
            except: pass
            print("[Gemini] HTTP " + str(e.code) + " cle=" +
                  str(idx+1) + " body=" + body[:100])

            if e.code == 429:
                errs = KS["errors"].get(idx, 0)
                wait = min(30 * (errs + 1), 120)
                set_cooldown(idx, wait)
                # Si une autre clé est dispo, rotation immédiate
                now = time.time()
                autre = any(
                    API_KEYS[i] and KS["model"].get(i) and
                    now >= KS["cooldowns"].get(i, 0)
                    for i in range(len(API_KEYS)) if i != idx
                )
                if not autre:
                    time.sleep(min(wait, 30))

            elif e.code == 403:
                forbidden = KS["forbidden"].setdefault(idx, set())
                forbidden.add(model)
                print("[Gemini] Modele " + model + " interdit cle " + str(idx+1))
                KS["model"][idx] = ""
                if not assign_model(idx):
                    set_cooldown(idx, 3600)

            elif e.code in (400, 404):
                forbidden = KS["forbidden"].setdefault(idx, set())
                forbidden.add(model)
                KS["model"][idx] = ""
                assign_model(idx)

            elif e.code == 503:
                time.sleep(15)

            else:
                time.sleep(10)

            last_err = "HTTP " + str(e.code)

        except TimeoutError:
            print("[Gemini] TIMEOUT " + str(timeout) + "s cle=" + str(idx+1))
            set_cooldown(idx, 30)
            last_err = "TIMEOUT"

        except Exception as ex:
            print("[Gemini] Erreur: " + str(ex))
            time.sleep(5)
            last_err = str(ex)

    print("[Gemini] ECHEC 5 tentatives. Derniere erreur: " + str(last_err))
    return None

# ══════════════════════════════════════════════════════
# DISCORD
# ══════════════════════════════════════════════════════
def discord_send(title, desc, color=0x5865F2, fields=None):
    if not DISCORD_WEBHOOK:
        print("[Discord] Webhook absent")
        return False

    # Modèle et clés actives
    cur_model = KS["model"].get(KS["current"], "?")
    now = time.time()
    active_n = sum(1 for i in range(len(API_KEYS))
                   if API_KEYS[i] and KS["model"].get(i) and
                   now >= KS["cooldowns"].get(i, 0))

    emb = {
        "title":       str(title)[:256],
        "description": str(desc)[:4096],
        "color":       color,
        "timestamp":   datetime.utcnow().isoformat() + "Z",
        "footer": {"text": (
            "MaxOS AI v9.0 | " + cur_model +
            " | " + str(active_n) + "/" + str(len(API_KEYS)) + " cles"
        )}
    }
    if fields:
        emb["fields"] = [
            {"name": str(f.get("name",""))[:256],
             "value": str(f.get("value","?"))[:1024],
             "inline": bool(f.get("inline", False))}
            for f in fields[:25]
        ]

    payload = json.dumps({
        "username": "MaxOS AI Bot",
        "embeds": [emb]
    }).encode("utf-8")

    req = urllib.request.Request(
        DISCORD_WEBHOOK, data=payload,
        headers={"Content-Type": "application/json",
                 "User-Agent": "MaxOS-Bot/9.0"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            if r.status in (200, 204):
                return True
    except urllib.error.HTTPError as e:
        body = ""
        try: body = e.read().decode()[:200]
        except: pass
        print("[Discord] HTTP " + str(e.code) + ": " + body)
        if e.code == 401:
            print("[Discord] WEBHOOK INVALIDE - regenerer le webhook")
    except Exception as ex:
        print("[Discord] " + str(ex))
    return False

def d(title, desc="", color=0x5865F2, fields=None):
    discord_send(title, desc, color, fields)

def pbar(pct, w=20):
    f = int(w * pct / 100)
    return "[" + "="*f + "-"*(w-f) + "] " + str(pct) + "%"

# ══════════════════════════════════════════════════════
# GITHUB API
# ══════════════════════════════════════════════════════
def gh(method, endpoint, data=None):
    if not GITHUB_TOKEN:
        return None
    url = ("https://api.github.com/repos/" +
           REPO_OWNER + "/" + REPO_NAME + "/" + endpoint)
    payload = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        url, data=payload,
        headers={
            "Authorization": "Bearer " + GITHUB_TOKEN,
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "MaxOS-AI/9.0",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        print("[GitHub] " + method + " " + endpoint + " -> HTTP " + str(e.code))
        return None
    except Exception as ex:
        print("[GitHub] " + str(ex))
        return None

def gh_release(tag, name, body, pre=False):
    r = gh("POST", "releases", {
        "tag_name": tag, "name": name, "body": body,
        "draft": False, "prerelease": pre
    })
    return r.get("html_url") if r and "html_url" in r else None

def gh_prs():
    r = gh("GET", "pulls?state=open&per_page=10")
    return r if isinstance(r, list) else []

def gh_merge(num, title):
    r = gh("PUT", "pulls/" + str(num) + "/merge", {
        "commit_title": "merge: " + title + " [AI]",
        "merge_method": "squash"
    })
    return bool(r and r.get("merged"))

def gh_comment(num, body):
    gh("POST", "issues/" + str(num) + "/comments", {"body": body})

def gh_close_pr(num):
    gh("PATCH", "pulls/" + str(num), {"state": "closed"})

def gh_latest_tag():
    r = gh("GET", "tags?per_page=1")
    if r and len(r) > 0:
        return r[0].get("name", "v0.0.0")
    return "v0.0.0"

# ══════════════════════════════════════════════════════
# FICHIERS DU PROJET
# ══════════════════════════════════════════════════════
BASE_FILES = [
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

SKIP_DIRS  = {".git", "build", "__pycache__", ".github", "ai_dev"}
SKIP_FILES = {"screen.h.save"}
SRC_EXTS   = {".c", ".h", ".asm", ".ld"}

def scan_files():
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
    src = {}
    all_files = sorted(set(BASE_FILES + scan_files()))
    for f in all_files:
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    src[f] = fh.read()
            except:
                src[f] = None
        else:
            src[f] = None
    return src

def proj_stats(src):
    files  = sum(1 for c in src.values() if c)
    lines  = sum(c.count("\n") for c in src.values() if c)
    return files, lines

def ctx_for_task(src, targets, max_c=25000):
    """Contexte ciblé: fichiers à modifier + dépendances."""
    out  = ""
    done = set()

    # 1. Fichiers cibles (complets)
    for f in targets:
        c = src.get(f, "")
        block = "=== " + f + " ===\n" + (c if c else "[A CREER]") + "\n\n"
        out += block
        done.add(f)
        # Header associé
        if f.endswith(".c"):
            h = f.replace(".c", ".h")
            if h not in done:
                hc = src.get(h, "")
                if hc:
                    out += "=== " + h + " ===\n" + hc + "\n\n"
                    done.add(h)

    # 2. Fichiers essentiels
    essentials = [
        "kernel/kernel.c", "Makefile", "linker.ld",
        "drivers/screen.h", "drivers/keyboard.h", "ui/ui.h"
    ]
    for f in essentials:
        if f in done: continue
        c = src.get(f, "")
        if not c: continue
        block = "=== " + f + " ===\n" + c + "\n\n"
        if len(out) + len(block) > max_c:
            out += "[" + f + " non inclus - trop grand]\n"
            continue
        out += block
        done.add(f)

    return out[:max_c]

# ══════════════════════════════════════════════════════
# GIT ET BUILD
# ══════════════════════════════════════════════════════
def git_run(args):
    r = subprocess.run(
        ["git"] + args, cwd=REPO_PATH,
        capture_output=True, text=True, timeout=60
    )
    return r.returncode == 0, r.stdout.strip(), r.stderr.strip()

def git_push(nom, files, desc, model):
    if not files:
        return True, None, None

    # Préfixe du commit
    dirs = set(f.split("/")[0] for f in files if "/" in f)
    pmap = {"kernel":"kernel","drivers":"driver","boot":"boot",
            "ui":"ui","apps":"feat","lib":"lib"}
    prefix = next((pmap[d] for d in pmap if d in dirs), "feat")

    fshort = ", ".join(os.path.basename(f) for f in files[:3])
    if len(files) > 3: fshort += " +" + str(len(files)-3)

    short = prefix + ": " + nom[:50] + " [" + fshort + "]"
    body  = (
        "\n\nFiles    : " + ", ".join(files) + "\n"
        "Model    : " + model + "\n"
        "Time     : " + datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") + "\n"
        "Desc     : " + desc[:150]
    )

    git_run(["add", "-A"])
    ok, out, err = git_run(["commit", "-m", short + body])
    if not ok:
        if "nothing to commit" in (out + err):
            return True, None, None
        print("[Git] Commit KO: " + err[:200])
        return False, None, None

    _, sha, _ = git_run(["rev-parse", "HEAD"])
    sha = sha[:7]

    ok2, _, e2 = git_run(["push"])
    if not ok2:
        # Retry avec pull --rebase
        git_run(["pull", "--rebase"])
        ok2, _, e2 = git_run(["push"])
        if not ok2:
            print("[Git] Push KO: " + e2[:200])
            return False, None, None

    print("[Git] Push OK: " + sha + " - " + short)
    return True, sha, short

def do_build():
    subprocess.run(["make", "clean"], cwd=REPO_PATH,
                   capture_output=True, timeout=30)
    r = subprocess.run(
        ["make"], cwd=REPO_PATH,
        capture_output=True, text=True, timeout=120
    )
    ok = r.returncode == 0
    log = (r.stdout + r.stderr)[-3000:]
    errs = [l.strip() for l in (r.stdout+r.stderr).split("\n")
            if "error:" in l.lower()][:15]
    print("[Build] " + ("OK" if ok else "ECHEC (" + str(len(errs)) + " err)"))
    for e in errs[:3]:
        print("  >> " + e[:100])
    return ok, log, errs

# ══════════════════════════════════════════════════════
# PARSER DE RÉPONSE
# ══════════════════════════════════════════════════════
def parse_response(text):
    """Parse les blocs FILE et DELETE dans la réponse Gemini."""
    files = {}
    dels  = []
    cur   = None
    lines = []
    in_f  = False

    for line in text.split("\n"):
        s = line.strip()

        # Début fichier
        if s.startswith("=== FILE:") and s.endswith("==="):
            raw = s[9:].rstrip("=").strip().strip("`").strip()
            if raw:
                cur = raw; lines = []; in_f = True
            continue

        # Fin fichier
        if s == "=== END FILE ===" and in_f:
            if cur:
                content = "\n".join(lines)
                # Retirer les balises de code markdown
                for lang in ["```c","```asm","```nasm",
                             "```makefile","```ld","```"]:
                    if content.lstrip().startswith(lang):
                        content = content.lstrip()[len(lang):]
                        break
                if content.rstrip().endswith("```"):
                    content = content.rstrip()[:-3]
                content = content.strip()
                if content:
                    files[cur] = content
                    print("[Parse] FILE: " + cur +
                          " (" + str(len(content)) + " chars)")
            cur = None; lines = []; in_f = False
            continue

        # Suppression
        if s.startswith("=== DELETE:") and s.endswith("==="):
            raw = s[11:].rstrip("=").strip()
            if raw:
                dels.append(raw)
                print("[Parse] DEL: " + raw)
            continue

        if in_f:
            lines.append(line)

    return files, dels

def write_files(files):
    written = []
    for path, content in files.items():
        if path.startswith("/") or ".." in path:
            print("[Write] SKIP chemin suspect: " + path)
            continue
        full = os.path.join(REPO_PATH, path)
        os.makedirs(os.path.dirname(full) or REPO_PATH, exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        print("[Write] " + path)
        written.append(path)
    return written

def del_files(paths):
    deleted = []
    for path in paths:
        if path.startswith("/") or ".." in path: continue
        full = os.path.join(REPO_PATH, path)
        if os.path.exists(full):
            os.remove(full)
            print("[Del] " + path)
            deleted.append(path)
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
    if bak:
        print("[Restore] " + str(len(bak)) + " fichier(s)")

# ══════════════════════════════════════════════════════
# PHASE 1: ANALYSE
# ══════════════════════════════════════════════════════
def analyse(src):
    print("\n[Analyse] Debut...")
    nf, nl = proj_stats(src)

    # Contexte léger pour l'analyse
    mini = ""
    for f in ["kernel/kernel.c", "Makefile", "ui/ui.c"]:
        c = src.get(f, "")
        if c:
            mini += "=== " + f + " (extrait) ===\n" + c[:800] + "\n\n"

    fichiers_ok = [f for f, c in src.items() if c]

    prompt = (
        RULES + "\n" + MISSION + "\n\n"
        "FICHIERS PRESENTS: " + ", ".join(fichiers_ok) + "\n"
        "STATS: " + str(nf) + " fichiers, " + str(nl) + " lignes\n\n"
        + mini +
        "\nANALYSE ET PLAN D'ACTION.\n"
        "Retourne UNIQUEMENT ce JSON valide (pas de texte avant/après):\n"
        '{\n'
        '  "score": 35,\n'
        '  "niveau": "Prototype bare metal",\n'
        '  "features": ["Boot x86", "VGA texte"],\n'
        '  "missing": ["IDT", "Timer PIT", "Mémoire"],\n'
        '  "milestone": "Kernel stable avec IDT+Timer",\n'
        '  "tasks": [\n'
        '    {\n'
        '      "nom": "Implémenter IDT 256 entrées + PIC 8259",\n'
        '      "prio": "CRITIQUE",\n'
        '      "cat": "kernel",\n'
        '      "mod": ["kernel/kernel.c", "kernel/kernel_entry.asm"],\n'
        '      "new": ["kernel/idt.h", "kernel/idt.c"],\n'
        '      "del": [],\n'
        '      "desc": "IDT 256 entrées, remappage PIC IRQ0-7->32-39, stubs NASM",\n'
        '      "impact": "OS stable sans triple fault",\n'
        '      "cx": "HAUTE"\n'
        '    }\n'
        '  ]\n'
        '}'
    )

    resp = gemini(prompt, max_tokens=3000, timeout=60)
    if not resp:
        print("[Analyse] Gemini KO, plan par defaut")
        return default_plan()

    # Parser JSON
    clean = resp.strip()
    # Retirer markdown
    if clean.startswith("```"):
        lines = clean.split("\n")
        clean = "\n".join(
            l for l in lines
            if not l.strip().startswith("```")
        ).strip()

    i = clean.find("{")
    j = clean.rfind("}") + 1
    if i >= 0 and j > i:
        try:
            data = json.loads(clean[i:j])
            # Normaliser les tâches
            tasks = []
            for t in data.get("tasks", []):
                tasks.append({
                    "nom":    t.get("nom", "Tache"),
                    "prio":   t.get("prio", "NORMALE"),
                    "cat":    t.get("cat", "general"),
                    "mod":    t.get("mod", []),
                    "new":    t.get("new", []),
                    "del":    t.get("del", []),
                    "desc":   t.get("desc", ""),
                    "impact": t.get("impact", ""),
                    "cx":     t.get("cx", "MOYENNE"),
                })
            data["tasks"] = tasks
            print("[Analyse] OK: score=" + str(data.get("score", "?")) +
                  " tasks=" + str(len(tasks)))
            return data
        except json.JSONDecodeError as e:
            print("[Analyse] JSON err: " + str(e))

    print("[Analyse] Plan par defaut")
    return default_plan()

def default_plan():
    return {
        "score":     35,
        "niveau":    "Prototype bare metal",
        "features":  ["Boot x86", "VGA texte", "Clavier PS/2", "4 apps"],
        "missing":   ["IDT", "Timer PIT", "Mémoire", "Mode graphique", "FAT12"],
        "milestone": "Kernel stable IDT+Timer",
        "tasks": [
            {
                "nom":    "IDT 256 entrées + PIC 8259 + gestionnaires exceptions",
                "prio":   "CRITIQUE", "cat": "kernel",
                "mod":    ["kernel/kernel.c", "kernel/kernel_entry.asm", "Makefile"],
                "new":    ["kernel/idt.h", "kernel/idt.c"],
                "del":    [],
                "desc":   ("IDT 256 entrées. PIC 8259 remappage IRQ0-7->32-39. "
                           "Stubs NASM vecteurs 0-47. Handlers exceptions 0-31. "
                           "panic() écran rouge. sti() à la fin."),
                "impact": "OS stable, plus de triple fault",
                "cx":     "HAUTE"
            },
            {
                "nom":    "Timer PIT 8253 100Hz + uptime + sleep_ms",
                "prio":   "CRITIQUE", "cat": "kernel",
                "mod":    ["kernel/kernel.c", "Makefile"],
                "new":    ["kernel/timer.h", "kernel/timer.c"],
                "del":    [],
                "desc":   ("PIT canal 0 diviseur 11931=100Hz. "
                           "Variable ticks volatile unsigned int. "
                           "timer_init() timer_ticks() sleep_ms(ms). "
                           "Uptime dans sysinfo."),
                "impact": "Horloge système, animations",
                "cx":     "MOYENNE"
            },
            {
                "nom":    "Terminal 20 commandes + historique flèches",
                "prio":   "HAUTE", "cat": "app",
                "mod":    ["apps/terminal.h", "apps/terminal.c"],
                "new":    [],
                "del":    [],
                "desc":   ("20 commandes: help ver mem uptime cls echo date "
                           "reboot halt color beep calc about sysinfo ps "
                           "license clear snake pong. "
                           "Historique 20 entrées flèche haut/bas."),
                "impact": "Terminal complet style cmd.exe",
                "cx":     "MOYENNE"
            },
            {
                "nom":    "Allocateur mémoire bitmap pages 4KB",
                "prio":   "HAUTE", "cat": "kernel",
                "mod":    ["kernel/kernel.c", "Makefile"],
                "new":    ["kernel/memory.h", "kernel/memory.c"],
                "del":    [],
                "desc":   ("Bitmap 1bit/page 4KB zone 1MB-16MB. "
                           "mem_init() mem_alloc() mem_free() "
                           "mem_used_kb() mem_total_kb(). "
                           "Stats dans sysinfo."),
                "impact": "Statistiques mémoire dans sysinfo",
                "cx":     "HAUTE"
            },
            {
                "nom":    "Mode VGA 320x200 256 couleurs + desktop",
                "prio":   "NORMALE", "cat": "driver",
                "mod":    ["drivers/screen.h", "drivers/screen.c",
                           "kernel/kernel.c", "Makefile"],
                "new":    ["drivers/vga.h", "drivers/vga.c"],
                "del":    [],
                "desc":   ("Mode 13h 320x200 0xA0000. "
                           "vga_init() vga_pixel(x,y,c) vga_rect() vga_clear(). "
                           "Desktop dégradé + taskbar. "
                           "Fallback mode texte si échec."),
                "impact": "Interface graphique colorée",
                "cx":     "HAUTE"
            },
        ]
    }

# ══════════════════════════════════════════════════════
# PHASE 2: IMPLÉMENTATION
# ══════════════════════════════════════════════════════
def implement(task, src):
    nom    = task["nom"]
    cat    = task["cat"]
    f_mod  = task.get("mod", [])
    f_new  = task.get("new", [])
    f_del  = task.get("del", [])
    desc   = task.get("desc", "")
    impact = task.get("impact", "")
    cx     = task.get("cx", "MOYENNE")
    targets = list(set(f_mod + f_new))

    model = KS["model"].get(KS["current"], "?")
    print("\n[Impl] " + nom)
    print("  Cat=" + cat + " Cx=" + cx)
    print("  Mod=" + str(f_mod))
    print("  New=" + str(f_new))
    if f_del:
        print("  Del=" + str(f_del))

    # Contexte ciblé
    ctx = ctx_for_task(src, targets)

    # Tokens selon complexité
    tok_map = {"HAUTE": 16384, "MOYENNE": 12288, "BASSE": 8192}
    max_tok = tok_map.get(cx, 12288)

    prompt = (
        RULES + "\n\n" + MISSION + "\n\n"
        "=== CONTEXTE ACTUEL ===\n" + ctx + "\n"
        "=== TACHE ===\n"
        "NOM:     " + nom + "\n"
        "CAT:     " + cat + " | COMPLEXITE: " + cx + "\n"
        "DESC:    " + desc + "\n"
        "IMPACT:  " + impact + "\n"
        "MODIFIER: " + json.dumps(f_mod) + "\n"
        "CREER:   " + json.dumps(f_new) + "\n"
        "SUPPRIMER: " + json.dumps(f_del) + "\n\n"
        "=== INSTRUCTIONS ===\n"
        "1. Code COMPLET et fonctionnel - JAMAIS '// reste inchangé' ou '...'\n"
        "2. Respecter TOUTES les règles bare metal\n"
        "3. Nouveaux .c -> les ajouter dans Makefile\n"
        "4. Code original, pas de copie\n"
        "5. Commenter les sections importantes\n\n"
        "=== FORMAT DE RÉPONSE (OBLIGATOIRE) ===\n"
        "=== FILE: chemin/fichier.ext ===\n"
        "[contenu complet du fichier]\n"
        "=== END FILE ===\n\n"
        "Génère maintenant le code:"
    )

    t0 = time.time()
    resp = gemini(prompt, max_tokens=max_tok, timeout=120)
    elapsed = round(time.time() - t0, 1)

    if not resp:
        d("❌ Echec: " + nom[:50],
          "Gemini n'a pas répondu après " + str(elapsed) + "s",
          0xFF4444)
        return False, [], []

    print("[Impl] Reponse: " + str(len(resp)) + " chars en " + str(elapsed) + "s")

    # Parser la réponse
    files, to_del = parse_response(resp)

    if not files and not to_del:
        print("[Impl] Rien parsé! Début réponse:")
        print(resp[:400])
        d("⚠️ Parse vide: " + nom[:50],
          "Réponse reçue mais aucun fichier parsé.", 0xFFA500)
        return False, [], []

    # Backup + écriture
    bak = backup_files(list(files.keys()))
    written = write_files(files)
    deleted = del_files(to_del)

    all_changed = written + deleted
    if not all_changed:
        return False, [], []

    # Build
    ok, log, errs = do_build()

    if ok:
        pushed, sha, _ = git_push(nom, all_changed, desc, model)
        if pushed:
            return True, written, deleted
        print("[Impl] Push KO, restauration")
        restore_files(bak)
        return False, [], []

    # Auto-fix (1 tentative)
    print("[Fix] Tentative correction...")
    fixed = auto_fix(log, errs, files, model)
    if fixed:
        _, sha, _ = git_push("fix: " + nom[:40], all_changed, desc, model)
        return True, written, deleted

    # Restauration
    restore_files(bak)
    for p in written:
        if p not in bak:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp):
                os.remove(fp)
    return False, [], []

# ══════════════════════════════════════════════════════
# AUTO-FIX
# ══════════════════════════════════════════════════════
def auto_fix(log, errs, gen_files, model):
    """Une seule tentative de fix rapide."""
    if not errs:
        return False

    # Lire les fichiers actuels
    curr = {}
    for p in gen_files:
        fp = os.path.join(REPO_PATH, p)
        if os.path.exists(fp):
            with open(fp, "r") as f:
                curr[p] = f.read()[:2000]

    ctx = "".join("=== " + p + " ===\n" + c + "\n\n"
                  for p, c in curr.items())
    err_str = "\n".join(errs[:8])

    prompt = (
        RULES + "\n\n"
        "ERREURS DE COMPILATION:\n```\n" + err_str + "\n```\n\n"
        "LOG (fin):\n```\n" + log[-800:] + "\n```\n\n"
        "FICHIERS GENERÉS:\n" + ctx +
        "\nCorrige UNIQUEMENT les erreurs. Code complet.\n\n"
        "=== FILE: fichier.ext ===\n[code corrigé]\n=== END FILE ==="
    )

    resp = gemini(prompt, max_tokens=12288, timeout=90)
    if not resp:
        return False

    files, _ = parse_response(resp)
    if not files:
        return False

    write_files(files)
    ok, _, _ = do_build()

    if ok:
        d("🔧 Auto-fix OK",
          str(len(errs)) + " erreur(s) corrigée(s)", 0x00AAFF)
        return True

    return False

# ══════════════════════════════════════════════════════
# PULL REQUESTS
# ══════════════════════════════════════════════════════
def handle_prs():
    prs = gh_prs()
    if not prs:
        print("[PR] Aucune PR ouverte")
        return

    print("[PR] " + str(len(prs)) + " PR(s) a traiter")
    for pr in prs[:5]:  # Max 5 PRs
        num    = pr.get("number")
        title  = pr.get("title", "")
        author = pr.get("user", {}).get("login", "")

        # Ignorer les PRs du bot
        if author in ("MaxOS-AI-Bot", "github-actions[bot]"):
            continue

        print("[PR] #" + str(num) + " par " + author + ": " + title)

        files_data = gh("GET", "pulls/" + str(num) + "/files") or []
        flist = "\n".join("- " + f.get("filename", "") for f in files_data[:10])

        prompt = (
            RULES + "\n\n"
            "PR #" + str(num) + " par " + author + "\n"
            "Titre: " + title + "\n"
            "Fichiers modifiés:\n" + flist + "\n\n"
            "Réponds UNIQUEMENT avec ce JSON:\n"
            '{"action":"MERGE","raison":"Code correct bare metal"}\n'
            "ou\n"
            '{"action":"REJECT","raison":"Utilise des libs standard"}\n\n'
            "MERGE si: code bare metal OK, pas de libs standard.\n"
            "REJECT si: #include stdio/stdlib/string, malloc, printf, etc."
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
            except:
                pass

        gh_comment(num, "## 🤖 Review AI\n\n**" + action + "**\n\n" + raison)

        if action == "MERGE":
            if gh_merge(num, title):
                d("✅ PR #" + str(num) + " mergée", title, 0x00FF88)
            else:
                d("⚠️ PR #" + str(num) + " merge échoué", title, 0xFFA500)
        else:
            gh_close_pr(num)
            d("❌ PR #" + str(num) + " rejetée", raison[:100], 0xFF4444)

# ══════════════════════════════════════════════════════
# RELEASE
# ══════════════════════════════════════════════════════
def make_release(done_tasks, failed_tasks, ana, nf, nl):
    if not GITHUB_TOKEN:
        return None

    last = gh_latest_tag()
    try:
        parts = [int(x) for x in last.lstrip("v").split(".")]
        while len(parts) < 3:
            parts.append(0)
        if len(done_tasks) >= 3:
            parts[1] += 1; parts[2] = 0
        else:
            parts[2] += 1
        new_tag = "v" + ".".join(str(x) for x in parts)
    except:
        new_tag = "v1.0.0"

    score   = ana.get("score", 30)
    niveau  = ana.get("niveau", "Prototype")
    ms      = ana.get("milestone", "")
    feats   = ana.get("features", [])
    now     = datetime.utcnow()

    # Modèles utilisés
    models_used = ", ".join(sorted(set(
        KS["model"].get(i, "") for i in range(len(API_KEYS))
        if KS["model"].get(i)
    )))

    # Changements
    changes = ""
    for t in done_tasks:
        sha  = t.get("sha", "")
        link = (" [`"+sha+"`](https://github.com/"+REPO_OWNER+"/"+REPO_NAME+
                "/commit/"+sha+")" if sha else "")
        changes += "- **" + t.get("nom", "") + "**" + link + "\n"
        fs = t.get("files", [])
        if fs:
            changes += "  - `" + "`, `".join(fs[:4]) + "`\n"

    failed_txt = "".join("- ~~" + t + "~~\n" for t in failed_tasks)
    feat_txt   = "\n".join("- " + f for f in feats)

    body = (
        "# MaxOS " + new_tag + "\n\n"
        "> 🤖 MaxOS AI Developer v9.0 - Objectif: Windows 11\n\n"
        "---\n\n"
        "## 📊 État\n\n"
        "| | |\n|---|---|\n"
        "| Score | **" + str(score) + "/100** |\n"
        "| Niveau | " + niveau + " |\n"
        "| Fichiers | " + str(nf) + " |\n"
        "| Lignes | " + str(nl) + " |\n"
        "| Milestone | " + ms + " |\n\n"
        "## ✅ Changements\n\n" + (changes or "- Maintenance\n") +
        ("\n## ⏭️ Reporté\n\n" + failed_txt if failed_txt else "") +
        "\n## 🧩 Fonctionnalités\n\n" + feat_txt + "\n\n"
        "---\n\n"
        "## 🚀 Tester MaxOS\n\n"
        "### Linux/WSL\n"
        "```bash\n"
        "sudo apt install qemu-system-x86\n"
        "qemu-system-i386 -drive format=raw,file=os.img,if=floppy "
        "-boot a -vga std -k fr -m 32 -no-reboot\n"
        "```\n\n"
        "### Windows (QEMU)\n"
        "```\n"
        "qemu-system-i386.exe -drive format=raw,file=os.img,if=floppy "
        "-boot a -vga std -k fr -m 32\n"
        "```\n\n"
        "### Compiler\n"
        "```bash\n"
        "sudo apt install nasm gcc make gcc-multilib\n"
        "git clone https://github.com/" + REPO_OWNER + "/" + REPO_NAME + "\n"
        "cd " + REPO_NAME + " && make\n"
        "```\n\n"
        "## ⌨️ Contrôles\n\n"
        "| Touche | Action |\n|---|---|\n"
        "| TAB | Changer d'app |\n"
        "| F1 | Bloc-Notes |\n"
        "| F2 | Terminal |\n"
        "| F3 | Sysinfo |\n"
        "| F4 | À propos |\n\n"
        "## ⚙️ Technique\n\n"
        "| | |\n|---|---|\n"
        "| Arch | x86 32-bit Protected Mode |\n"
        "| CC | GCC -m32 -ffreestanding -nostdlib |\n"
        "| ASM | NASM ELF32 |\n"
        "| IA | " + models_used + " |\n\n"
        "---\n"
        "*MaxOS AI v9.0 | " + now.strftime("%Y-%m-%d %H:%M") + " UTC*\n"
    )

    url = gh_release(
        new_tag,
        "MaxOS " + new_tag + " | " + niveau + " | " + now.strftime("%Y-%m-%d"),
        body,
        pre=(score < 50)
    )

    if url:
        d("🚀 Release " + new_tag,
          "Score: " + str(score) + "/100 | " + niveau,
          0x00FF88,
          [{"name": "Version",  "value": new_tag, "inline": True},
           {"name": "Score",    "value": str(score)+"/100", "inline": True},
           {"name": "Release",  "value": "[Voir](" + url + ")", "inline": False}])
        print("[Release] " + new_tag + " -> " + url)

    return url

# ══════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════
def main():
    print("=" * 55)
    print("  MaxOS AI Developer v9.0")
    print("  Rapide | Robuste | Zéro timeout")
    print("=" * 55 + "\n")

    # Init des clés (sans appels test)
    if not init_all():
        print("FATAL: Aucune clé Gemini configurée")
        sys.exit(1)

    # Message de démarrage Discord
    d("🤖 MaxOS AI v9.0 démarré",
      str(len([i for i in range(len(API_KEYS)) if KS["model"].get(i)])) +
      "/" + str(len(API_KEYS)) + " clés prêtes",
      0x5865F2,
      [{"name": "Clés",  "value": keys_info(), "inline": False},
       {"name": "Repo",  "value": REPO_OWNER + "/" + REPO_NAME, "inline": True}])

    # Traiter les PRs
    print("\n[PRs] Vérification...")
    handle_prs()

    # Lire les sources
    src = read_all()
    nf, nl = proj_stats(src)
    print("[Sources] " + str(nf) + " fichiers, " + str(nl) + " lignes")

    # ── Phase 1: Analyse ──
    print("\n" + "=" * 55)
    print(" PHASE 1: Analyse du projet")
    print("=" * 55)

    ana   = analyse(src)
    score = ana.get("score", 30)
    niveau   = ana.get("niveau", "?")
    tasks    = ana.get("tasks", [])
    milestone = ana.get("milestone", "?")
    features  = ana.get("features", [])
    missing   = ana.get("missing", [])

    print("[Analyse] Score=" + str(score) + " | " + niveau)
    print("[Analyse] " + str(len(tasks)) + " tâche(s) | " + milestone)

    # Trier par priorité
    prio_order = {"CRITIQUE": 0, "HAUTE": 1, "NORMALE": 2, "BASSE": 3}
    tasks = sorted(tasks, key=lambda t: prio_order.get(t.get("prio","NORMALE"), 2))

    d("📊 Score " + str(score) + "/100 - " + niveau,
      "```\n" + pbar(score) + "\n```",
      0x00AAFF if score >= 60 else 0xFFA500 if score >= 30 else 0xFF4444,
      [{"name": "✅ Présentes",
        "value": "\n".join("+ " + f for f in features[:5]) or "?",
        "inline": True},
       {"name": "❌ Manquantes",
        "value": "\n".join("- " + f for f in missing[:5]) or "?",
        "inline": True},
       {"name": "📋 Plan",
        "value": "\n".join(
            "["+str(i+1)+"] ["+t.get("prio","?")+"] "+t.get("nom","?")[:40]
            for i, t in enumerate(tasks[:5])
        ), "inline": False},
       {"name": "🎯 Milestone", "value": milestone[:80], "inline": False},
       {"name": "🔑 Clés",     "value": keys_info(),    "inline": False}])

    # ── Phase 2: Implémentation ──
    print("\n" + "=" * 55)
    print(" PHASE 2: Implémentation")
    print("=" * 55)

    total   = len(tasks)
    success = 0
    done_tasks   = []
    failed_tasks = []

    for i, task in enumerate(tasks, 1):
        nom   = task.get("nom", "Tache " + str(i))
        prio  = task.get("prio", "NORMALE")
        cat   = task.get("cat", "?")
        model = KS["model"].get(KS["current"], "?")

        print("\n" + "=" * 55)
        print("[" + str(i) + "/" + str(total) + "] [" + prio + "] " + nom)
        print("=" * 55)

        pct_start = int((i-1) / total * 100)

        d("[" + str(i) + "/" + str(total) + "] " + nom[:60],
          "```\n" + pbar(pct_start) + "\n```\n" +
          task.get("desc", "")[:120] + "...",
          0xFFA500,
          [{"name": "Priorité", "value": prio,  "inline": True},
           {"name": "Catégorie","value": cat,   "inline": True},
           {"name": "Modèle",   "value": model, "inline": True}])

        # Relire les sources à chaque tâche
        src = read_all()
        ok, written, deleted = implement(task, src)

        # SHA du dernier commit
        _, sha_raw, _ = git_run(["rev-parse", "HEAD"])
        sha = sha_raw[:7] if sha_raw else "?"

        if ok:
            success += 1
            done_tasks.append({
                "nom":   nom,
                "sha":   sha,
                "files": written + deleted,
                "model": model
            })
            all_f = written + deleted
            d("✅ Succès: " + nom[:50],
              "Commit `" + sha + "`",
              0x00FF88,
              [{"name": "📝 Écrits",
                "value": "\n".join("`"+f+"`" for f in written[:5]) or "Aucun",
                "inline": True},
               {"name": "🗑️ Supprimés",
                "value": "\n".join("`"+f+"`" for f in deleted) or "Aucun",
                "inline": True},
               {"name": "📊 Progress",
                "value": pbar(int(i/total*100)),
                "inline": False}])
        else:
            failed_tasks.append(nom)
            d("❌ Echec: " + nom[:50],
              "Code restauré. Suite du plan...",
              0xFF6600)

        # Pause entre les tâches
        if i < total:
            now = time.time()
            n_ok = sum(1 for ii in range(len(API_KEYS))
                       if API_KEYS[ii] and
                       KS["model"].get(ii) and
                       now >= KS["cooldowns"].get(ii, 0))
            # Pause courte si plusieurs clés dispo
            pause = 10 if n_ok >= 2 else 20
            print("[Pause] " + str(pause) + "s...")
            time.sleep(pause)

    # ── Release ──
    if success > 0:
        print("\n[Release] Création...")
        src2 = read_all()
        nf2, nl2 = proj_stats(src2)
        make_release(done_tasks, failed_tasks, ana, nf2, nl2)

    # ── Résumé final ──
    pct_final = int(success / total * 100) if total > 0 else 0
    color_final = (0x00FF88 if pct_final >= 80
                   else 0xFFA500 if pct_final >= 50
                   else 0xFF4444)

    print("\n" + "=" * 55)
    print("[FIN] " + str(success) + "/" + str(total) + " tâches réussies")
    print("=" * 55)

    d("🏁 Cycle terminé - " + str(success) + "/" + str(total),
      "```\n" + pbar(pct_final) + "\n```",
      color_final,
      [{"name": "✅ Succès",  "value": str(success),          "inline": True},
       {"name": "❌ Échecs",  "value": str(total - success),   "inline": True},
       {"name": "📈 Taux",    "value": str(pct_final) + "%",   "inline": True},
       {"name": "🔑 Clés",    "value": keys_info(),            "inline": False}])

if __name__ == "__main__":
    main()
