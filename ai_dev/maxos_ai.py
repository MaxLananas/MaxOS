#!/usr/bin/env python3
"""MaxOS AI Developer v8.3 - Stable, anti-429, Discord fiable"""

import os, sys, json, time, subprocess, re
import urllib.request, urllib.error
from datetime import datetime

# ══════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════
def load_keys():
    keys = []
    k = os.environ.get("GEMINI_API_KEY", "")
    if k:
        keys.append(k)
    for i in range(2, 10):
        k = os.environ.get("GEMINI_API_KEY_" + str(i), "")
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

print("[v8.3] " + str(len(API_KEYS)) + " cle(s) Gemini")
for i,k in enumerate(API_KEYS):
    print("  Cle " + str(i+1) + ": " + mask(k))
print("[v8.3] Discord: " + ("OK" if DISCORD_WEBHOOK else "ABSENT - verifie le secret"))
print("[v8.3] GitHub:  " + ("OK" if GITHUB_TOKEN else "NON"))
print("[v8.3] Repo:    " + REPO_OWNER + "/" + REPO_NAME)

if not API_KEYS:
    print("FATAL: GEMINI_API_KEY manquante")
    sys.exit(1)

# ══════════════════════════════════════════════════════
# ETAT GLOBAL DES CLES
# ══════════════════════════════════════════════════════
# Pour chaque cle: modele actif, cooldown, nb appels
KEY_STATE = {
    "idx":        0,       # cle courante
    "cooldowns":  {},      # idx -> timestamp fin cooldown
    "calls":      {},      # idx -> nb appels reussis
    "errors":     {},      # idx -> nb erreurs 429
    "forbidden":  {},      # idx -> set modeles 403
}
ACTIVE = {}  # idx -> {"model": str, "url": str}

# Modeles par ordre de preference (lite en 1er = moins de quota)
MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.5-pro",
]

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

# ══════════════════════════════════════════════════════
# REGLES ET MISSION
# ══════════════════════════════════════════════════════
RULES = """REGLES BARE METAL x86 ABSOLUES:
- ZERO: #include <stddef.h> <string.h> <stdlib.h> <stdio.h> <stdint.h> <stdbool.h>
- ZERO: size_t NULL bool true false uint32_t malloc memset strlen printf
- TOUT remplacer: size_t->uint, NULL->0, bool->int, 1/0 au lieu de true/false
- gcc -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie
- nasm -f elf pour .o, nasm -f bin pour boot.bin
- ld -m elf_i386 -T linker.ld --oformat binary
- Nouveaux .c -> ajouter dans Makefile
- L'IA PEUT creer, modifier, supprimer des fichiers

SIGNATURES EXISTANTES A RESPECTER:
  nb_init() nb_draw() nb_key(char k)
  tm_init() tm_draw() tm_key(char k)
  si_draw()  ab_draw()
  kb_init() kb_haskey() kb_getchar()
  v_init() v_put() v_str() v_fill()"""

MISSION = """MISSION MAXOS: Devenir un OS complet (objectif Windows 11).
L'IA developpe seule, 24h/24. Elle peut creer/modifier/supprimer tout fichier.
Priorites: IDT+PIC > Timer PIT > Memoire > Mode graphique > Apps > FAT12 > Reseau"""

# ══════════════════════════════════════════════════════
# ROTATION CLES - VERSION SIMPLE ET ROBUSTE
# ══════════════════════════════════════════════════════
def next_key():
    """Trouve la prochaine cle disponible. Attend si besoin."""
    now = time.time()
    n = len(API_KEYS)

    for delta in range(n):
        idx = (KEY_STATE["idx"] + delta) % n
        if not API_KEYS[idx]:
            continue
        cd = KEY_STATE["cooldowns"].get(idx, 0)
        if now >= cd:
            KEY_STATE["idx"] = idx
            KEY_STATE["calls"][idx] = KEY_STATE["calls"].get(idx, 0) + 1
            return idx

    # Toutes en cooldown
    valid = [i for i in range(n) if API_KEYS[i]]
    best = min(valid, key=lambda i: KEY_STATE["cooldowns"].get(i, 0))
    wait = KEY_STATE["cooldowns"].get(best, 0) - now + 1
    print("[Keys] Attente " + str(int(wait)) + "s...")
    time.sleep(max(wait, 1))
    KEY_STATE["idx"] = best
    return best

def put_cooldown(idx, secs):
    KEY_STATE["cooldowns"][idx] = time.time() + secs
    KEY_STATE["errors"][idx] = KEY_STATE["errors"].get(idx, 0) + 1
    n = len(API_KEYS)
    if n > 1:
        nxt = (idx + 1) % n
        for _ in range(n):
            if API_KEYS[nxt]:
                break
            nxt = (nxt + 1) % n
        KEY_STATE["idx"] = nxt
        print("[Keys] Cle " + str(idx+1) + " cooldown " +
              str(secs) + "s -> cle " + str(nxt+1))
    else:
        print("[Keys] Cle 1 cooldown " + str(secs) + "s")

def keys_info():
    now = time.time()
    lines = []
    for i in range(len(API_KEYS)):
        if not API_KEYS[i]: continue
        cd = KEY_STATE["cooldowns"].get(i, 0)
        st = "OK" if now >= cd else "CD " + str(int(cd-now)) + "s"
        m = ACTIVE.get(i, {}).get("model", "?")
        c = KEY_STATE["calls"].get(i, 0)
        lines.append("Cle " + str(i+1) + ": " + st + " | " + str(c) + " appels | " + m)
    return "\n".join(lines) if lines else "Aucune cle"

# ══════════════════════════════════════════════════════
# INIT MODELE - LAZY, SANS APPEL TEST
# ══════════════════════════════════════════════════════
def init_key(idx):
    """
    N'envoie PLUS de requete test.
    Configure juste l'URL avec le premier modele non-interdit.
    """
    if idx >= len(API_KEYS) or not API_KEYS[idx]:
        return False
    key = API_KEYS[idx]
    forbidden = KEY_STATE["forbidden"].get(idx, set())

    for model in MODELS:
        if model in forbidden:
            continue
        url = ("https://generativelanguage.googleapis.com/v1beta/models/" +
               model + ":generateContent?key=" + key)
        print("[Gemini] Cle " + str(idx+1) + " -> " + model + " (lazy)")
        ACTIVE[idx] = {"model": model, "url": url}
        return True

    print("[Gemini] Cle " + str(idx+1) + " : tous modeles interdits")
    return False

def init_all():
    """Init sans test = zero quota consomme."""
    print("[Gemini] Initialisation lazy...")
    ok = 0
    for i in range(len(API_KEYS)):
        if API_KEYS[i]:
            if init_key(i):
                ok += 1
    print("[Gemini] " + str(ok) + "/" + str(len(API_KEYS)) + " cle(s) configurees")
    return ok > 0

def init_all():
    print("[Gemini] Initialisation...")
    ok = 0
    for i in range(len(API_KEYS)):
        if API_KEYS[i]:
            if init_key(i):
                ok += 1
            time.sleep(1)
    print("[Gemini] " + str(ok) + "/" + str(len(API_KEYS)) + " cle(s) OK")
    return ok > 0

# ══════════════════════════════════════════════════════
# APPEL GEMINI - ROBUSTE ET ANTI-429
# ══════════════════════════════════════════════════════
def gemini(prompt, max_tokens=32768):
    if not ACTIVE:
        if not init_all():
            return None

    if len(prompt) > 48000:
        prompt = prompt[:48000] + "\n[TRONQUE]"

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.1
        }
    }).encode("utf-8")

    for attempt in range(1, 9):
        idx = next_key()

        # Init lazy si pas encore configure
        if idx not in ACTIVE:
            if not init_key(idx):
                put_cooldown(idx, 300)
                continue

        info = ACTIVE[idx]
        key = API_KEYS[idx]
        url = info["url"].split("?")[0] + "?key=" + key

        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read().decode())
                cands = data.get("candidates", [])
                if not cands:
                    # Verifier finishReason au niveau root
                    reason = data.get("promptFeedback",{}).get("blockReason","")
                    print("[Gemini] Pas de candidates, blockReason=" + reason)
                    continue

                c = cands[0]
                finish = c.get("finishReason", "STOP")

                if finish in ("SAFETY", "RECITATION"):
                    print("[Gemini] Reponse bloquee: " + finish)
                    if finish == "RECITATION" and attempt <= 3:
                        prompt = ("Ecris une implementation originale:\n\n" +
                                  prompt[-2000:])
                        time.sleep(3)
                        continue
                    return None

                parts = c.get("content", {}).get("parts", [])
                texts = [p.get("text","") for p in parts
                         if isinstance(p, dict)
                         and not p.get("thought")
                         and p.get("text")]
                text = "".join(texts)

                if not text:
                    print("[Gemini] Vide (finish=" + finish + ")")
                    if "MAX_TOKENS" in finish and max_tokens > 8192:
                        max_tokens = max_tokens // 2
                        continue
                    # Essayer modele suivant
                    cur = info.get("model","")
                    if idx not in KEY_STATE["forbidden"]:
                        KEY_STATE["forbidden"][idx] = set()
                    KEY_STATE["forbidden"][idx].add(cur)
                    if idx in ACTIVE:
                        del ACTIVE[idx]
                    init_key(idx)
                    continue

                print("[Gemini] Cle " + str(idx+1) + " OK -> " +
                      str(len(text)) + " chars (" + finish + ")")
                return text

        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode()[:200]
            except:
                pass
            print("[Gemini] Cle " + str(idx+1) +
                  " HTTP " + str(e.code) +
                  " attempt=" + str(attempt) +
                  " body=" + body[:80])

            if e.code == 429:
                errs = KEY_STATE["errors"].get(idx, 0)
                # Cooldown progressif: 60s, 120s, 180s...
                wait = min(60 * (errs + 1), 300)
                put_cooldown(idx, wait)

                # Verifier si une autre cle est dispo
                now = time.time()
                autres_dispo = any(
                    API_KEYS[i] and now >= KEY_STATE["cooldowns"].get(i, 0)
                    for i in range(len(API_KEYS)) if i != idx
                )
                if not autres_dispo:
                    # Attendre le minimum
                    min_wait = min(
                        KEY_STATE["cooldowns"].get(i, 0) - now
                        for i in range(len(API_KEYS)) if API_KEYS[i]
                    )
                    actual_wait = max(min(min_wait + 1, 60), 5)
                    print("[Gemini] Toutes cles en CD, attente " +
                          str(int(actual_wait)) + "s")
                    time.sleep(actual_wait)

            elif e.code == 403:
                # Ce modele est interdit pour cette cle
                cur_model = ACTIVE.get(idx, {}).get("model", "")
                if cur_model:
                    if idx not in KEY_STATE["forbidden"]:
                        KEY_STATE["forbidden"][idx] = set()
                    KEY_STATE["forbidden"][idx].add(cur_model)
                    print("[Gemini] Cle " + str(idx+1) +
                          " modele " + cur_model + " interdit -> suivant")
                if idx in ACTIVE:
                    del ACTIVE[idx]
                # Essayer modele suivant sur meme cle
                if not init_key(idx):
                    put_cooldown(idx, 3600)  # Toute la cle inutilisable

            elif e.code in (400, 404):
                print("[Gemini] Erreur config " + str(e.code))
                if idx in ACTIVE:
                    del ACTIVE[idx]
                init_key(idx)

            elif e.code == 503:
                print("[Gemini] Service indisponible, attente 30s")
                time.sleep(30)

            else:
                time.sleep(20)

        except Exception as e:
            print("[Gemini] Exception: " + str(e))
            time.sleep(10)

    print("[Gemini] ECHEC apres 8 tentatives")
    return None

# ══════════════════════════════════════════════════════
# DISCORD - ROBUSTE
# ══════════════════════════════════════════════════════
def discord_send(title, desc, color=0x5865F2, fields=None):
    """Envoie un message Discord. Ne crash pas si le webhook est mort."""
    if not DISCORD_WEBHOOK:
        print("[Discord] Webhook absent - verifie le secret DISCORD_WEBHOOK")
        return False

    # Construire le footer
    cur_model = ACTIVE.get(KEY_STATE["idx"], {}).get("model", "?")
    active_n = sum(1 for i in range(len(API_KEYS))
                   if API_KEYS[i] and
                   time.time() >= KEY_STATE["cooldowns"].get(i, 0))

    emb = {
        "title": str(title)[:256],
        "description": str(desc)[:4096],
        "color": color,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "footer": {"text": (
            "MaxOS AI v8.3 | " + cur_model +
            " | " + str(active_n) + "/" + str(len(API_KEYS)) + " cles"
        )}
    }
    if fields:
        emb["fields"] = fields[:25]

    payload = json.dumps({
        "username": "MaxOS AI Bot",
        "embeds": [emb]
    }).encode("utf-8")

    req = urllib.request.Request(
        DISCORD_WEBHOOK, data=payload,
        headers={"Content-Type": "application/json",
                 "User-Agent": "MaxOS-Bot/8.3"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print("[Discord] OK (" + str(r.status) + ")")
            return True
    except urllib.error.HTTPError as e:
        body = ""
        try: body = e.read().decode()
        except: pass
        print("[Discord] HTTP " + str(e.code) + ": " + body[:100])
        if e.code == 403:
            print("[Discord] WEBHOOK INVALIDE - recreer le webhook Discord")
            print("[Discord] et mettre a jour le secret DISCORD_WEBHOOK")
    except Exception as e:
        print("[Discord] Erreur: " + str(e))
    return False

def d(title, desc, color=0x5865F2, fields=None):
    discord_send(title, desc, color, fields)

def pbar(pct, w=24):
    f = int(w * pct / 100)
    return "[" + "X"*f + "-"*(w-f) + "] " + str(pct) + "%"

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
            "User-Agent": "MaxOS-AI/8.3",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        print("[GitHub] " + method + " " + endpoint + " -> " + str(e.code))
        return None
    except Exception as e:
        print("[GitHub] " + str(e))
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

# ══════════════════════════════════════════════════════
# SOURCES
# ══════════════════════════════════════════════════════
def scan_files():
    found = []
    exts = {".c", ".h", ".asm", ".ld", ".py"}
    skip = {".git", "build", "__pycache__", ".github"}
    bad = {"screen.h.save"}
    for root, dirs, files in os.walk(REPO_PATH):
        dirs[:] = [d for d in dirs if d not in skip]
        for f in files:
            if f in bad: continue
            if os.path.splitext(f)[1] in exts or f == "Makefile":
                rel = os.path.relpath(
                    os.path.join(root, f), REPO_PATH
                ).replace("\\", "/")
                found.append(rel)
    return sorted(found)

def read_all():
    src = {}
    for f in sorted(set(BASE_FILES + scan_files())):
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                src[f] = fh.read()
        else:
            src[f] = None
    return src

def ctx_compact(src, max_c=32000):
    """Contexte compact: index + fichiers importants en premier."""
    out = "FICHIERS:\n"
    for f,c in src.items():
        out += ("  [OK] " if c else "  [--] ") + f + "\n"
    out += "\n"
    used = len(out)

    # Priorite: kernel, Makefile, drivers headers, ui
    prio = ["kernel/kernel.c","Makefile","linker.ld",
            "kernel/kernel_entry.asm","boot/boot.asm",
            "drivers/screen.h","drivers/keyboard.h",
            "ui/ui.h","ui/ui.c"]
    done = set()

    for f in prio:
        c = src.get(f,"")
        if not c: continue
        block = "=== " + f + " ===\n" + c + "\n\n"
        if used + len(block) > max_c: continue
        out += block; used += len(block); done.add(f)

    for f,c in src.items():
        if f in done or not c: continue
        block = "=== " + f + " ===\n" + c + "\n\n"
        if used + len(block) > max_c:
            out += "[" + f + " tronque]\n"
            continue
        out += block; used += len(block)

    return out

def proj_stats(src):
    f = sum(1 for c in src.values() if c)
    l = sum(c.count("\n") for c in src.values() if c)
    return f, l

# ══════════════════════════════════════════════════════
# GIT ET BUILD
# ══════════════════════════════════════════════════════
def git(args):
    r = subprocess.run(
        ["git"] + args, cwd=REPO_PATH,
        capture_output=True, text=True
    )
    return r.returncode == 0, r.stdout, r.stderr

def make_commit_msg(nom, files, desc, model):
    dirs = set(f.split("/")[0] for f in files if "/" in f)
    pmap = {"kernel":"kernel","drivers":"driver","boot":"boot",
            "ui":"ui","apps":"feat(apps)"}
    prefix = next((pmap[d] for d in pmap if d in dirs), "feat")
    fshort = ", ".join(os.path.basename(f) for f in files[:3])
    if len(files) > 3: fshort += " +" + str(len(files)-3)
    short = prefix + ": " + nom + " [" + fshort + "]"
    body = (
        "\n\nComponent : " + ", ".join(sorted(dirs)) + "\n"
        "Files     : " + ", ".join(files) + "\n"
        "Model     : " + model + "\n"
        "Timestamp : " + datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") + "\n"
        "\nDescription:\n  " + desc[:200] + "\n"
        "\narch: x86-32 | gcc -m32 -ffreestanding | nasm ELF32"
    )
    return short, short + body

def do_push(nom, files, desc, model):
    if not files: return True, None, None
    short, full = make_commit_msg(nom, files, desc, model)
    git(["add", "-A"])
    ok, out, err = git(["commit", "-m", full])
    if not ok:
        if "nothing to commit" in (out+err):
            return True, None, None
        print("[Git] Commit KO: " + err[:150])
        return False, None, None
    _, sha, _ = git(["rev-parse", "HEAD"])
    sha = sha.strip()[:7]
    ok2, _, e2 = git(["push"])
    if not ok2:
        print("[Git] Push KO: " + e2[:150])
        return False, None, None
    print("[Git] " + sha + ": " + short)
    return True, sha, short

def do_build():
    subprocess.run(["make","clean"], cwd=REPO_PATH, capture_output=True)
    r = subprocess.run(
        ["make"], cwd=REPO_PATH,
        capture_output=True, text=True, timeout=120
    )
    ok = r.returncode == 0
    log = r.stdout + r.stderr
    errs = [l.strip() for l in log.split("\n") if "error:" in l.lower()]
    print("[Build] " + ("OK" if ok else "ECHEC") +
          " (" + str(len(errs)) + " err)")
    if not ok:
        for e in errs[:5]: print("  " + e)
    return ok, log, errs[:12]

# ══════════════════════════════════════════════════════
# PARSER
# ══════════════════════════════════════════════════════
def parse(response):
    files = {}
    dels = []
    cur = None
    lines = []
    infile = False

    for line in response.split("\n"):
        s = line.strip()

        if "=== FILE:" in s and s.endswith("==="):
            try:
                fname = s[s.index("=== FILE:")+9:s.rindex("===")].strip().strip("`")
                if fname:
                    cur = fname; lines = []; infile = True
            except: pass
            continue

        if s == "=== END FILE ===" and infile:
            if cur:
                content = "\n".join(lines).strip()
                for lang in ["```c","```asm","```nasm","```makefile","```ld","```"]:
                    if content.startswith(lang):
                        content = content[len(lang):].lstrip("\n"); break
                if content.endswith("```"):
                    content = content[:-3].rstrip("\n")
                if content.strip():
                    files[cur] = content
                    print("[Parse] " + cur + " (" + str(len(content)) + "c)")
            cur = None; lines = []; infile = False
            continue

        if "=== DELETE:" in s and s.endswith("==="):
            try:
                fname = s[s.index("=== DELETE:")+11:s.rindex("===")].strip()
                if fname: dels.append(fname); print("[Parse] DEL: " + fname)
            except: pass
            continue

        if infile: lines.append(line)

    return files, dels

def write_files(files):
    written = []
    for path, content in files.items():
        if path.startswith("/") or ".." in path: continue
        full = os.path.join(REPO_PATH, path)
        os.makedirs(os.path.dirname(full) or REPO_PATH, exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        written.append(path)
        print("[Write] " + path)
    return written

def del_files(paths):
    deleted = []
    for path in paths:
        if path.startswith("/") or ".." in path: continue
        full = os.path.join(REPO_PATH, path)
        if os.path.exists(full):
            os.remove(full); deleted.append(path)
            print("[Del] " + path)
    return deleted

def backup(paths):
    b = {}
    for p in paths:
        full = os.path.join(REPO_PATH, p)
        if os.path.exists(full):
            with open(full,"r",encoding="utf-8",errors="ignore") as f:
                b[p] = f.read()
    return b

def restore(bak):
    for p,c in bak.items():
        full = os.path.join(REPO_PATH, p)
        os.makedirs(os.path.dirname(full) or REPO_PATH, exist_ok=True)
        with open(full,"w",encoding="utf-8") as f: f.write(c)
    print("[Restore] " + str(len(bak)) + " fichier(s)")

# ══════════════════════════════════════════════════════
# PHASE 1: ANALYSE (prompt compact)
# ══════════════════════════════════════════════════════
def analyse(src):
    print("\n[Analyse] Debut...")
    nf, nl = proj_stats(src)

    # Contexte minimal
    mini_ctx = ""
    for f in ["kernel/kernel.c","Makefile","ui/ui.c","apps/terminal.c"]:
        c = src.get(f,"")
        if c: mini_ctx += "=== " + f + " ===\n" + c[:1500] + "\n\n"

    prompt = (
        RULES + "\n" + MISSION + "\n\n"
        "FICHIERS: " + ", ".join(f for f,c in src.items() if c) + "\n"
        "Stats: " + str(nf) + " fichiers, " + str(nl) + " lignes\n\n"
        + mini_ctx +
        "Retourne ce JSON (commence par {, rien avant):\n"
        '{"score":35,"niveau":"Prototype","features":["Boot","VGA"],'
        '"missing":["IDT","Timer"],'
        '"tasks":[{"nom":"Nom","prio":"CRITIQUE","cat":"kernel",'
        '"mod":["kernel/kernel.c"],"new":["kernel/idt.h","kernel/idt.c"],'
        '"del":[],"desc":"Description technique complete",'
        '"impact":"Impact visible QEMU","cx":"HAUTE"}],'
        '"milestone":"Kernel stable"}'
    )

    resp = gemini(prompt, max_tokens=2500)
    if not resp: return None

    print("[Analyse] " + str(len(resp)) + " chars")
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
                data = json.loads(clean[i:j])
                # Normaliser vers plan_ameliorations
                plan = []
                for t in data.get("tasks", []):
                    plan.append({
                        "nom": t.get("nom","?"),
                        "priorite": t.get("prio","NORMALE"),
                        "categorie": t.get("cat","general"),
                        "fichiers_a_modifier": t.get("mod",[]),
                        "fichiers_a_creer": t.get("new",[]),
                        "fichiers_a_supprimer": t.get("del",[]),
                        "description": t.get("desc",""),
                        "impact": t.get("impact",""),
                        "complexite": t.get("cx","MOYENNE"),
                    })
                data["plan"] = plan
                return data
            except json.JSONDecodeError as e:
                print("[Analyse] JSON err: " + str(e))
                idx = clean.find("{")
                if idx > 0: clean = clean[idx:]

    # Plan par defaut
    print("[Analyse] Plan par defaut")
    return {
        "score": 35, "niveau": "Prototype bare metal",
        "features": ["Boot x86","VGA texte","Clavier PS/2","4 apps"],
        "missing": ["IDT","Timer PIT","Memoire","Mode graphique","FAT12"],
        "milestone": "Kernel stable IDT+Timer+Memory",
        "plan": [
            {
                "nom": "IDT 256 entrees + PIC 8259 + handlers x86",
                "priorite": "CRITIQUE", "categorie": "kernel",
                "fichiers_a_modifier": ["kernel/kernel.c","kernel/kernel_entry.asm","Makefile"],
                "fichiers_a_creer": ["kernel/idt.h","kernel/idt.c"],
                "fichiers_a_supprimer": [],
                "description": ("IDT 256 entrees. PIC 8259 remappage "
                    "IRQ0-7->INT32-39, IRQ8-15->INT40-47. "
                    "Stubs NASM pour vecteurs 0-47. "
                    "Handlers exceptions 0-31 avec message. "
                    "panic() affiche ecran rouge."),
                "impact": "OS stable sans triple fault",
                "complexite": "HAUTE"
            },
            {
                "nom": "Timer PIT 8253 100Hz + sleep_ms + uptime",
                "priorite": "CRITIQUE", "categorie": "kernel",
                "fichiers_a_modifier": ["kernel/kernel.c","Makefile"],
                "fichiers_a_creer": ["kernel/timer.h","kernel/timer.c"],
                "fichiers_a_supprimer": [],
                "description": ("PIT canal 0 diviseur 11931 = 100Hz. "
                    "Variable ticks globale volatile. "
                    "timer_init() timer_ticks() sleep_ms(ms). "
                    "Uptime HH:MM:SS dans sysinfo."),
                "impact": "Horloge systeme, animations fluides",
                "complexite": "MOYENNE"
            },
            {
                "nom": "Terminal 20 commandes + historique fleches",
                "priorite": "HAUTE", "categorie": "app",
                "fichiers_a_modifier": ["apps/terminal.h","apps/terminal.c"],
                "fichiers_a_creer": [],
                "fichiers_a_supprimer": [],
                "description": ("20 commandes: help ver mem uptime cls echo "
                    "date reboot halt color beep calc about credits "
                    "sysinfo ps license clear snake pong. "
                    "Historique circulaire 20 entrees fleche haut/bas. "
                    "Prompt colore avec heure."),
                "impact": "Terminal type cmd.exe complet",
                "complexite": "MOYENNE"
            },
            {
                "nom": "Allocateur memoire bitmap pages 4KB",
                "priorite": "HAUTE", "categorie": "kernel",
                "fichiers_a_modifier": ["kernel/kernel.c","Makefile"],
                "fichiers_a_creer": ["kernel/memory.h","kernel/memory.c"],
                "fichiers_a_supprimer": [],
                "description": ("Bitmap 1bit/page 4KB zone 1MB-16MB. "
                    "mem_init() mem_alloc() mem_free() "
                    "mem_used_kb() mem_total_kb(). "
                    "Stats dans sysinfo."),
                "impact": "Stats memoire visibles dans sysinfo",
                "complexite": "HAUTE"
            },
            {
                "nom": "Mode graphique VGA 320x200 + desktop colore",
                "priorite": "NORMALE", "categorie": "driver",
                "fichiers_a_modifier": [
                    "drivers/screen.h","drivers/screen.c",
                    "kernel/kernel.c","Makefile"
                ],
                "fichiers_a_creer": ["drivers/vga.h","drivers/vga.c"],
                "fichiers_a_supprimer": [],
                "description": ("Mode 13h 320x200 256 couleurs 0xA0000. "
                    "vga_init() vga_pixel(x,y,c) vga_rect() vga_text(). "
                    "Desktop fond degrade, taskbar bas. "
                    "Fallback mode texte si echec init."),
                "impact": "Interface graphique coloree",
                "complexite": "HAUTE"
            },
        ]
    }

# ══════════════════════════════════════════════════════
# PHASE 2: IMPLEMENTATION
# ══════════════════════════════════════════════════════
def implement(task, src):
    nom = task.get("nom","?")
    cat = task.get("categorie","?")
    f_mod = task.get("fichiers_a_modifier",[])
    f_new = task.get("fichiers_a_creer",[])
    f_del = task.get("fichiers_a_supprimer",[])
    desc = task.get("description","")
    impact = task.get("impact","")
    cx = task.get("complexite","MOYENNE")
    targets = list(set(f_mod + f_new))

    model = ACTIVE.get(KEY_STATE["idx"],{}).get("model","?")

    print("\n[Impl] " + nom)
    print("  " + cat + " | " + cx)
    print("  Mod: " + str(f_mod))
    print("  New: " + str(f_new))

    # Contexte cible uniquement
    tctx = ""
    done = set()
    for f in targets:
        c = src.get(f,"")
        tctx += "=== " + f + " ===\n" + (c if c else "[A CREER]") + "\n\n"
        done.add(f)
        # Header associe
        partner = f.replace(".c",".h") if f.endswith(".c") else ""
        if partner and partner not in done:
            pc = src.get(partner,"")
            if pc: tctx += "=== " + partner + " ===\n" + pc + "\n\n"; done.add(partner)

    # Fichiers essentiels toujours inclus
    for ess in ["kernel/kernel.c","Makefile","drivers/screen.h",
                "drivers/keyboard.h","ui/ui.h","linker.ld"]:
        if ess not in done:
            c = src.get(ess,"")
            if c: tctx += "=== " + ess + " ===\n" + c + "\n\n"; done.add(ess)

    if len(tctx) > 22000:
        tctx = tctx[:22000] + "\n[TRONQUE]\n"

    prompt = (
        RULES + "\n\n" + MISSION + "\n\n"
        "CONTEXTE:\n" + tctx +
        "TACHE: " + nom + "\n"
        "CAT: " + cat + " | COMPLEXITE: " + cx + "\n"
        "DESC: " + desc + "\n"
        "IMPACT: " + impact + "\n"
        "MODIFIER: " + str(f_mod) + "\n"
        "CREER: " + str(f_new) + "\n"
        "SUPPRIMER: " + str(f_del) + "\n\n"
        "INSTRUCTIONS:\n"
        "1. Code COMPLET - jamais '// reste inchange' ou '...'\n"
        "2. Nouveaux .c -> ajouter dans Makefile\n"
        "3. Code original (pas de copie)\n"
        "4. Commenter les sections cles\n\n"
        "FORMAT REPONSE:\n"
        "=== FILE: chemin/fichier.c ===\n"
        "[code complet]\n"
        "=== END FILE ===\n\n"
        "COMMENCE:"
    )

    max_tok = 49152 if cx == "HAUTE" else 32768
    t0 = time.time()
    resp = gemini(prompt, max_tokens=max_tok)
    t1 = time.time()

    if not resp:
        d("Echec: " + nom, "Gemini n'a pas repondu.", 0xFF4444)
        return False, [], []

    print("[Impl] " + str(len(resp)) + " chars en " + str(round(t1-t0,1)) + "s")

    files, to_del = parse(resp)

    if not files and not to_del:
        print("[Debug] " + resp[:300])
        return False, [], []

    bak = backup(list(files.keys()))
    written = write_files(files)
    deleted = del_files(to_del)

    if not written and not deleted:
        return False, [], []

    ok, log, errs = do_build()

    if ok:
        pushed, sha, _ = do_push(nom, written+deleted, desc, model)
        if pushed:
            return True, written, deleted
        restore(bak)
        return False, [], []

    # Auto-fix
    if auto_fix(log, errs, files, bak, model):
        return True, written, deleted

    restore(bak)
    for p in written:
        if p not in bak:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp): os.remove(fp)
    return False, [], []

# ══════════════════════════════════════════════════════
# AUTO-FIX
# ══════════════════════════════════════════════════════
def auto_fix(log, errs, gen_files, bak, model):
    print("[Fix] " + str(len(errs)) + " erreurs...")

    for attempt in range(1, 3):
        curr = {}
        for p in gen_files:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp):
                with open(fp,"r") as f: curr[p] = f.read()

        ctx = "".join("=== " + p + " ===\n" + c[:2000] + "\n\n"
                      for p,c in curr.items())
        err_txt = "\n".join(errs[:10])

        prompt = (
            RULES + "\n\n"
            "ERREURS:\n```\n" + err_txt + "\n```\n\n"
            "LOG:\n```\n" + log[-1000:] + "\n```\n\n"
            "FICHIERS:\n" + ctx +
            "Corrige les erreurs. Code complet.\n\n"
            "=== FILE: fichier.c ===\n[code]\n=== END FILE ==="
        )

        resp = gemini(prompt, max_tokens=24576)
        if not resp: continue

        files, _ = parse(resp)
        if not files: continue

        write_files(files)
        ok, log2, new_errs = do_build()

        if ok:
            do_push("fix: correction compilation",
                    list(files.keys()),
                    "Auto-fix: " + str(len(errs)) + " erreurs -> 0", model)
            d("Auto-fix reussi",
              str(len(errs)) + " erreurs corrigees.", 0x00AAFF)
            return True

        errs = new_errs
        time.sleep(15)

    restore(bak)
    return False

# ══════════════════════════════════════════════════════
# PULL REQUESTS
# ══════════════════════════════════════════════════════
def handle_prs():
    prs = gh_prs()
    if not prs: return
    print("[PR] " + str(len(prs)) + " PR(s)")
    for pr in prs:
        num = pr.get("number")
        title = pr.get("title","")
        author = pr.get("user",{}).get("login","")
        if author in ("github-actions","MaxOS-AI-Bot"): continue

        files_data = gh("GET","pulls/"+str(num)+"/files") or []
        flist = "\n".join("- "+f.get("filename","") for f in files_data[:10])

        prompt = (
            RULES + "\n\nPR #" + str(num) + ": " + title +
            "\nAuteur: " + author + "\nFichiers:\n" + flist +
            '\n\nJSON: {"action":"MERGE","raison":"ok"}\n'
            "MERGE si bare metal OK. REJECT si libs standard.\n{"
        )
        resp = gemini(prompt, max_tokens=200)
        action, raison = "REJECT", "Analyse impossible"
        if resp:
            try:
                txt = ("{" + resp) if not resp.strip().startswith("{") else resp
                i = txt.find("{"); j = txt.rfind("}")+1
                dec = json.loads(txt[i:j])
                action = dec.get("action","REJECT")
                raison = dec.get("raison","")
            except: pass

        gh_comment(num, "## Review AI\n**" + action + "** - " + raison)
        if action == "MERGE":
            if gh_merge(num, title):
                d("PR #"+str(num)+" mergee", title, 0x00FF88)
        else:
            gh_close_pr(num)
            d("PR #"+str(num)+" rejetee", title, 0xFF4444)

# ══════════════════════════════════════════════════════
# RELEASE
# ══════════════════════════════════════════════════════
def make_release(done, failed, ana, nf, nl):
    if not GITHUB_TOKEN: return None

    r = gh("GET","tags?per_page=1")
    last = r[0].get("name","v0.0.0") if r and len(r)>0 else "v0.0.0"
    try:
        parts = [int(x) for x in last.lstrip("v").split(".")]
        if len(done) >= 3: parts[1] += 1; parts[2] = 0
        else: parts[2] += 1
        new_tag = "v" + ".".join(str(x) for x in parts)
    except: new_tag = "v1.0.0"

    now = datetime.utcnow()
    score = ana.get("score",30)
    niveau = ana.get("niveau","Prototype")
    milestone = ana.get("milestone","")
    features = ana.get("features",[])
    models = ", ".join(set(
        ACTIVE.get(i,{}).get("model","") for i in range(len(API_KEYS))
        if i in ACTIVE and ACTIVE[i].get("model")
    ))

    changes = ""
    for t in done:
        sha = t.get("sha","")
        sha_lnk = (" [`"+sha+"`](https://github.com/"+REPO_OWNER+"/"+REPO_NAME+"/commit/"+sha+")"
                   if sha else "")
        changes += "- **" + t.get("nom","") + "**" + sha_lnk + "\n"
        if t.get("files"):
            changes += "  - `" + "`, `".join(t["files"][:4]) + "`\n"

    failed_txt = "".join("- ~~"+t+"~~\n" for t in failed)
    feat_txt = "\n".join("- "+f for f in features)

    body = (
        "# MaxOS " + new_tag + "\n\n"
        "> MaxOS AI Developer v8.3 - Objectif: Windows 11 scale\n\n"
        "---\n\n## Etat\n\n"
        "| | |\n|---|---|\n"
        "| Score | **"+str(score)+"/100** |\n"
        "| Niveau | "+niveau+" |\n"
        "| Fichiers | "+str(nf)+" |\n"
        "| Lignes | "+str(nl)+" |\n"
        "| Milestone | "+milestone+" |\n\n"
        "## Changements\n\n"+(changes or "- Maintenance\n")+
        ("\n## Reporte\n\n"+failed_txt if failed_txt else "")+
        "\n## Fonctionnalites\n\n"+feat_txt+"\n\n"
        "---\n\n## Tester MaxOS\n\n"
        "### Telecharger os.img\n"
        "```\nGitHub -> Actions -> Dernier run -> Artifacts -> maxos-build-XXX\n```\n\n"
        "### Lancer (Linux/WSL)\n"
        "```bash\nsudo apt install qemu-system-x86\n"
        "qemu-system-i386 -drive format=raw,file=os.img,if=floppy "
        "-boot a -vga std -k fr -m 32 -no-reboot\n```\n\n"
        "### Lancer (Windows - QEMU installe)\n"
        "```\nqemu-system-i386.exe -drive format=raw,file=os.img,if=floppy "
        "-boot a -vga std -k fr -m 32\n```\n\n"
        "### Compiler (WSL)\n"
        "```bash\nsudo apt install nasm gcc make gcc-multilib qemu-system-x86\n"
        "git clone https://github.com/"+REPO_OWNER+"/"+REPO_NAME+"\n"
        "cd MaxOS && make && make run\n```\n\n"
        "## Controles\n\n"
        "| Touche | Action |\n|---|---|\n"
        "| TAB | Changer d'app |\n| F1 | Bloc-Notes |\n"
        "| F2 | Terminal |\n| F3 | Sysinfo |\n| F4 | A propos |\n\n"
        "## Technique\n\n"
        "| | |\n|---|---|\n"
        "| Arch | x86 32-bit Protected Mode |\n"
        "| CC | GCC -m32 -ffreestanding -nostdlib |\n"
        "| ASM | NASM ELF32 |\n"
        "| IA | "+models+" |\n\n"
        "## Roadmap\n\n"
        "| Phase | Statut | Objectif |\n|---|---|---|\n"
        "| 1 | En cours | IDT + Timer + Memoire |\n"
        "| 2 | Planifie | Mode graphique VESA |\n"
        "| 3 | Planifie | FAT12 |\n"
        "| 4 | Planifie | GUI fenetres + souris |\n"
        "| 5 | Planifie | Applications |\n"
        "| 6 | Futur | TCP/IP |\n\n"
        "*MaxOS AI v8.3 | "+now.strftime("%Y-%m-%d %H:%M")+" UTC*\n"
    )

    url = gh_release(
        new_tag,
        "MaxOS "+new_tag+" - "+niveau+" | "+now.strftime("%Y-%m-%d"),
        body, pre=(score<50)
    )
    if url:
        d("Release "+new_tag+" publiee",
          "Score: "+str(score)+"/100 | "+niveau, 0x00FF88,
          [{"name":"Version","value":new_tag,"inline":True},
           {"name":"Score","value":str(score)+"/100","inline":True},
           {"name":"Lien","value":"[Release]("+url+")","inline":False}])
    return url

# ══════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════
def main():
    print("="*55)
    print("  MaxOS AI Developer v8.3")
    print("  Stable | Anti-429 | Discord fiable")
    print("="*55+"\n")

    # Init
    if not init_all():
        print("FATAL: Aucune cle Gemini OK")
        sys.exit(1)

    d("MaxOS AI v8.3 demarre",
      str(len(ACTIVE))+"/"+str(len(API_KEYS))+" cles actives",
      0x5865F2,
      [{"name":"Cles","value":keys_info(),"inline":False},
       {"name":"Repo","value":REPO_OWNER+"/"+REPO_NAME,"inline":True}])

    # PRs
    print("\n[PRs] Check...")
    handle_prs()

    # Sources
    src = read_all()
    nf, nl = proj_stats(src)
    print("[Sources] "+str(nf)+" fichiers, "+str(nl)+" lignes")

    # Analyse
    print("\n"+"="*55+"\n PHASE 1: Analyse\n"+"="*55)
    ana = analyse(src)
    if not ana:
        d("Analyse echouee","Impossible d'analyser.",0xFF0000)
        sys.exit(1)

    score = ana.get("score",30)
    niveau = ana.get("niveau","?")
    plan = ana.get("plan",[])
    milestone = ana.get("milestone","?")
    features = ana.get("features",[])
    missing = ana.get("missing",[])

    print("[Analyse] "+str(score)+"/100 | "+niveau)
    print("[Analyse] "+str(len(plan))+" taches | "+milestone)

    d("Score "+str(score)+"/100 - "+niveau,
      "```\n"+pbar(score)+"\n```",
      0x00AAFF if score>=60 else 0xFFA500 if score>=30 else 0xFF4444,
      [{"name":"Presentes",
        "value":"\n".join("+ "+f for f in features[:4]) or "?",
        "inline":True},
       {"name":"Manquantes",
        "value":"\n".join("- "+f for f in missing[:4]) or "?",
        "inline":True},
       {"name":"Plan",
        "value":"\n".join(
            "["+str(i+1)+"] ["+t.get("priorite","?")+"] "+t.get("nom","?")[:35]
            for i,t in enumerate(plan[:5])
        ),"inline":False},
       {"name":"Milestone","value":milestone[:80],"inline":False},
       {"name":"Cles","value":keys_info(),"inline":False}])

    # Implementation
    print("\n"+"="*55+"\n PHASE 2: Implementation\n"+"="*55)

    order = {"CRITIQUE":0,"HAUTE":1,"NORMALE":2,"BASSE":3}
    plan = sorted(plan, key=lambda x: order.get(x.get("priorite","NORMALE"),2))

    success = 0
    total = len(plan)
    done = []
    failed = []

    for i, task in enumerate(plan, 1):
        nom = task.get("nom","Tache "+str(i))
        prio = task.get("priorite","NORMALE")
        cat = task.get("categorie","?")

        print("\n"+"="*55)
        print("["+str(i)+"/"+str(total)+"] ["+prio+"] "+nom)
        print("="*55)

        model = ACTIVE.get(KEY_STATE["idx"],{}).get("model","?")

        d("["+str(i)+"/"+str(total)+"] "+nom,
          "```\n"+pbar(int((i-1)/total*100))+"\n```\n"+
          task.get("description","")[:150],
          0xFFA500,
          [{"name":"Prio","value":prio,"inline":True},
           {"name":"Cat","value":cat,"inline":True},
           {"name":"Model","value":model,"inline":True}])

        src = read_all()
        ok, written, deleted = implement(task, src)

        _, sha_raw, _ = git(["rev-parse","HEAD"])
        sha = sha_raw.strip()[:7] if sha_raw.strip() else "?"

        if ok:
            success += 1
            done.append({
                "nom": nom, "sha": sha,
                "files": written+deleted, "model": model
            })
            d("Succes: "+nom, "Commit `"+sha+"`", 0x00FF88,
              [{"name":"Ecrits",
                "value":"\n".join("`"+f+"`" for f in written[:4]) or "Aucun",
                "inline":True},
               {"name":"Supprimes",
                "value":"\n".join("`"+f+"`" for f in deleted) or "Aucun",
                "inline":True}])
            src = read_all()
        else:
            failed.append(nom)
            d("Echec: "+nom,"Code restaure.",0xFF6600)

        if i < total:
            # Pause intelligente
            n_ok = sum(1 for ii in range(len(API_KEYS))
                       if API_KEYS[ii] and
                       time.time() >= KEY_STATE["cooldowns"].get(ii,0))
            pause = 15 if n_ok > 1 else 30
            print("[Pause] "+str(pause)+"s...")
            time.sleep(pause)

    # Release
    if success > 0:
        src = read_all()
        nf2, nl2 = proj_stats(src)
        make_release(done, failed, ana, nf2, nl2)

    pct = int(success/total*100) if total > 0 else 0
    color = 0x00FF88 if pct>=80 else 0xFFA500 if pct>=50 else 0xFF4444

    d("Cycle fini - "+str(success)+"/"+str(total),
      "```\n"+pbar(pct)+"\n```",
      color,
      [{"name":"Succes","value":str(success),"inline":True},
       {"name":"Echecs","value":str(total-success),"inline":True},
       {"name":"Taux","value":str(pct)+"%","inline":True},
       {"name":"Cles","value":keys_info(),"inline":False}])

    print("\n[FIN] "+str(success)+"/"+str(total))

if __name__ == "__main__":
    main()
