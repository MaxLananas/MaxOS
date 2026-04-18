#!/usr/bin/env python3
"""MaxOS AI Developer v8.1 - Corrections cles + modeles"""

import os, sys, json, time, subprocess, re
import urllib.request, urllib.error
from datetime import datetime

# ══════════════════════════════════════════════════════
# CONFIGURATION MULTI-CLES
# ══════════════════════════════════════════════════════
def load_api_keys():
    keys = []
    k1 = os.environ.get("GEMINI_API_KEY", "")
    if k1:
        keys.append(k1)
    for i in range(2, 10):
        k = os.environ.get("GEMINI_API_KEY_" + str(i), "")
        if k:
            keys.append(k)
    return keys

API_KEYS = load_api_keys()

# GITHUB_TOKEN est fourni automatiquement par GitHub Actions.
# C'est ${{ secrets.GITHUB_TOKEN }} dans le workflow.
# Tu n'as PAS besoin de creer ce secret manuellement.
GITHUB_TOKEN    = os.environ.get("GH_PAT", "") or os.environ.get("GITHUB_TOKEN", "")
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")
REPO_OWNER      = os.environ.get("REPO_OWNER", "MaxLananas")
REPO_NAME       = os.environ.get("REPO_NAME", "MaxOS")
REPO_PATH       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KEY_STATE = {
    "current_index": 0,
    "cooldowns":     {},
    "usage_count":   {},
    "errors":        {},
    "working_models": {},  # key_idx -> liste de modeles qui marchent
}

def mask_key(k):
    if len(k) > 8:
        return k[:4] + "*" * max(0, len(k) - 8) + k[-4:]
    return "***"

print("[Config] Cles Gemini : " + str(len(API_KEYS)) + " cle(s) chargee(s)")
for i, k in enumerate(API_KEYS):
    print("         Cle " + str(i+1) + " : " + mask_key(k))
print("[Config] Discord : " + ("OK" if DISCORD_WEBHOOK else "ABSENT"))
print("[Config] GitHub  : " + ("OK" if GITHUB_TOKEN else "ABSENT"))
print("[Config] Repo    : " + REPO_OWNER + "/" + REPO_NAME)
print("[Config] Path    : " + REPO_PATH)

if not API_KEYS:
    print("FATAL: Aucune GEMINI_API_KEY trouvee")
    sys.exit(1)

# ══════════════════════════════════════════════════════
# MODELES - lite en premier pour eviter 429
# ══════════════════════════════════════════════════════
# On met lite en premier : moins de quota consomme,
# moins de 429, disponible sur plan gratuit
MODELS_PRIORITY = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.5-pro",
    "gemini-1.5-flash-latest",
]

ACTIVE_MODELS = {}  # key_idx -> {"model": str, "url": str}

# ══════════════════════════════════════════════════════
# FICHIERS DU PROJET
# ══════════════════════════════════════════════════════
ALL_FILES = [
    "boot/boot.asm",
    "kernel/kernel_entry.asm",
    "kernel/kernel.c",
    "drivers/screen.h",
    "drivers/screen.c",
    "drivers/keyboard.h",
    "drivers/keyboard.c",
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

# ══════════════════════════════════════════════════════
# MISSION
# ══════════════════════════════════════════════════════
OS_MISSION = """
MISSION MAXOS - OBJECTIF OS COMPLET TYPE WINDOWS 11

L'IA est le developpeur principal, autonome 24h/24 7j/7.
L'IA peut creer, supprimer et modifier n'importe quel fichier du projet.

PRIORITES D'IMPLEMENTATION :

COUCHE 1 - KERNEL :
  - IDT complete 256 entrees + handlers exceptions x86 (0-31)
  - PIC 8259 initialise (IRQ 0-15 remappes)
  - Timer PIT 8253 a 100Hz + sleep() + uptime
  - Gestionnaire memoire physique bitmap 4KB
  - Appels systeme basiques

COUCHE 2 - DRIVERS :
  - Clavier PS/2 complet (Shift, Ctrl, Alt, fleches, F1-F12)
  - VGA texte 80x25 couleurs ameliore
  - VGA graphique mode 13h (320x200, 256 couleurs)
  - Son PC speaker (beeps, notes musicales)
  - Souris PS/2

COUCHE 3 - SYSTEME FICHIERS :
  - FAT12 lecture/ecriture sur disquette
  - VFS abstrait

COUCHE 4 - GUI :
  - Fenetres avec titre, bordures, boutons fermer/min/max
  - Z-order, fenetres empilees
  - Curseur souris avec rendu
  - Desktop avec fond d'ecran degrade
  - Taskbar style Windows 11
  - Menu demarrer avec icones

COUCHE 5 - APPLICATIONS :
  - Terminal 20+ commandes (help,ver,mem,uptime,cls,echo,
    reboot,halt,color,ls,cat,mkdir,rm,edit,calc,beep,ps,date)
  - Editeur texte avec curseur clignotant + sauvegarde
  - Gestionnaire taches (liste processus, memoire)
  - Calculatrice avec interface
  - Horloge/calendrier
  - Jeux: Snake, Tetris, Pong
  - Editeur hexadecimal

COUCHE 6 - RESEAU :
  - Driver NE2000 (QEMU)
  - Stack TCP/IP minimale
  - DHCP client, Ping

REGLES ABSOLUES :
- Chaque modification doit compiler dans QEMU
- Code C bare metal pur, zero librairie standard
- Mettre a jour Makefile si nouveaux fichiers .c crees
- Stabilite avant complexite
"""

BARE_METAL_RULES = """
REGLES BARE METAL x86 ABSOLUES :

1. ZERO include standard :
   PAS <stddef.h> <string.h> <stdlib.h> <stdio.h> <stdint.h> <stdbool.h>

2. ZERO types standard :
   size_t -> unsigned int
   NULL -> 0
   bool -> int, true/false -> 1/0
   uint32_t -> unsigned int

3. ZERO fonctions standard :
   malloc/free, memset/memcpy, strlen/strcmp, printf/sprintf

4. SIGNATURES EXISTANTES (ne pas changer) :
   nb_init(), nb_draw(), nb_key(char k)
   tm_init(), tm_draw(), tm_key(char k)
   si_draw()
   ab_draw()
   kb_init(), kb_haskey(), kb_getchar()
   v_init(), v_put(), v_str(), v_fill()

5. COMPILATION :
   gcc -m32 -ffreestanding -fno-stack-protector -fno-builtin
       -fno-pic -fno-pie -nostdlib -nostdinc -w -c
   nasm -f elf / nasm -f bin
   ld -m elf_i386 -T linker.ld --oformat binary

6. L'IA PEUT :
   - Creer nouveaux fichiers .c/.h/.asm
   - Supprimer fichiers obsoletes
   - Modifier Makefile
   - Restructurer le projet
"""

# ══════════════════════════════════════════════════════
# ROTATION DES CLES
# ══════════════════════════════════════════════════════
def get_best_key():
    now = time.time()
    n = len(API_KEYS)
    # Chercher une cle sans cooldown
    for attempt in range(n):
        idx = (KEY_STATE["current_index"] + attempt) % n
        if API_KEYS[idx] and now >= KEY_STATE["cooldowns"].get(idx, 0):
            KEY_STATE["current_index"] = idx
            KEY_STATE["usage_count"][idx] = (
                KEY_STATE["usage_count"].get(idx, 0) + 1
            )
            return idx
    # Toutes en cooldown -> attendre la moins longue
    valid = [i for i in range(n) if API_KEYS[i]]
    if not valid:
        print("FATAL: Aucune cle valide")
        sys.exit(1)
    min_idx = min(valid, key=lambda i: KEY_STATE["cooldowns"].get(i, 0))
    wait = KEY_STATE["cooldowns"].get(min_idx, 0) - now + 1
    print("[Keys] Attente " + str(int(wait)) + "s (cle " + str(min_idx+1) + ")")
    time.sleep(max(wait, 1))
    return min_idx

def set_key_cooldown(key_idx, seconds):
    KEY_STATE["cooldowns"][key_idx] = time.time() + seconds
    KEY_STATE["errors"][key_idx] = KEY_STATE["errors"].get(key_idx, 0) + 1
    n = len(API_KEYS)
    if n > 1:
        next_idx = (key_idx + 1) % n
        # Sauter les cles vides
        for _ in range(n):
            if API_KEYS[next_idx]:
                break
            next_idx = (next_idx + 1) % n
        KEY_STATE["current_index"] = next_idx
        print("[Keys] Cle " + str(key_idx+1) + " cooldown " +
              str(seconds) + "s -> cle " + str(next_idx+1))
    else:
        print("[Keys] Cle unique cooldown " + str(seconds) + "s")

def key_status_str():
    now = time.time()
    lines = []
    for i in range(len(API_KEYS)):
        if not API_KEYS[i]:
            continue
        cd = KEY_STATE["cooldowns"].get(i, 0)
        usage = KEY_STATE["usage_count"].get(i, 0)
        err = KEY_STATE["errors"].get(i, 0)
        status = "OK" if now >= cd else "CD " + str(int(cd - now)) + "s"
        model = ACTIVE_MODELS.get(i, {}).get("model", "?")
        lines.append("Cle " + str(i+1) + ": " + status +
                     " | " + str(usage) + " req | " +
                     str(err) + " err | " + model)
    return "\n".join(lines) if lines else "Aucune cle"

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
            "Authorization": "Bearer " + GITHUB_TOKEN,
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "MaxOS-AI-Bot",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print("[GitHub] " + method + " " + endpoint +
              " HTTP " + str(e.code) + ": " + body[:150])
        return None
    except Exception as e:
        print("[GitHub] " + str(e))
        return None

def github_create_release(tag, name, body, prerelease=False):
    data = {
        "tag_name": tag,
        "name": name,
        "body": body,
        "draft": False,
        "prerelease": prerelease,
    }
    r = github_api("POST", "releases", data)
    if r and "html_url" in r:
        print("[GitHub] Release: " + r["html_url"])
        return r["html_url"]
    return None

def github_get_open_prs():
    r = github_api("GET", "pulls?state=open&per_page=10")
    return r if isinstance(r, list) else []

def github_merge_pr(pr_number, title):
    data = {
        "commit_title": "merge: " + title + " [AI]",
        "merge_method": "squash"
    }
    r = github_api("PUT", "pulls/" + str(pr_number) + "/merge", data)
    return bool(r and r.get("merged"))

def github_comment_pr(pr_number, body):
    github_api("POST", "issues/" + str(pr_number) + "/comments",
               {"body": body})

def github_close_pr(pr_number):
    github_api("PATCH", "pulls/" + str(pr_number), {"state": "closed"})

# ══════════════════════════════════════════════════════
# DISCORD
# ══════════════════════════════════════════════════════
def discord_send(embeds):
    if not DISCORD_WEBHOOK:
        return
    payload = json.dumps({
        "username": "MaxOS AI Bot",
        "embeds": embeds[:10]
    }).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WEBHOOK, data=payload,
        headers={"Content-Type": "application/json",
                 "User-Agent": "DiscordBot"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15):
            return True
    except Exception as e:
        print("[Discord] " + str(e))
    return False

def make_embed(title, desc, color, fields=None):
    now = time.time()
    active = sum(1 for i in range(len(API_KEYS))
                 if API_KEYS[i] and now >= KEY_STATE["cooldowns"].get(i, 0))
    cur_model = ACTIVE_MODELS.get(
        KEY_STATE["current_index"], {}
    ).get("model", "init")
    e = {
        "title": str(title)[:256],
        "description": str(desc)[:4096],
        "color": color,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "footer": {
            "text": ("MaxOS AI v8.1 | " + cur_model +
                     " | " + str(active) + "/" + str(len(API_KEYS)) +
                     " cles | " + REPO_OWNER + "/" + REPO_NAME)
        },
    }
    if fields:
        e["fields"] = fields[:25]
    return e

def d(title, desc, color=0x5865F2, fields=None):
    discord_send([make_embed(title, desc, color, fields)])

def progress_bar(pct, w=28):
    f = int(w * pct / 100)
    return "[" + ("X" * f) + ("-" * (w - f)) + "] " + str(pct) + "%"

# ══════════════════════════════════════════════════════
# GEMINI - AVEC GESTION DU BUG 'parts'
# ══════════════════════════════════════════════════════
def extract_text_from_response(data):
    """
    Extrait le texte d'une reponse Gemini.
    Gere les cas:
    - Reponse normale avec parts
    - Modeles "thinking" qui ont des parts multiples
    - finishReason OTHER ou RECITATION
    """
    try:
        candidates = data.get("candidates", [])
        if not candidates:
            print("[Gemini] Pas de candidates dans la reponse")
            return None

        candidate = candidates[0]
        finish = candidate.get("finishReason", "STOP")

        if finish in ("SAFETY", "RECITATION"):
            print("[Gemini] Reponse bloquee: " + finish)
            return None

        content = candidate.get("content", {})
        parts = content.get("parts", [])

        if not parts:
            print("[Gemini] Pas de parts (finishReason=" + finish + ")")
            # Parfois le modele retourne quand meme du texte dans content
            text = content.get("text", "")
            if text:
                return text
            return None

        # Concatener tous les parts de type text
        # (les modeles thinking ont des parts "thought" + "text")
        texts = []
        for part in parts:
            if isinstance(part, dict):
                # Ignorer les parts "thought" (thinking models)
                if part.get("thought"):
                    continue
                t = part.get("text", "")
                if t:
                    texts.append(t)

        result = "".join(texts)
        if not result:
            print("[Gemini] Parts presents mais aucun texte extrait")
            return None

        return result

    except Exception as e:
        print("[Gemini] Erreur extraction: " + str(e))
        return None

def find_model_for_key(key_idx):
    """Trouve le meilleur modele pour une cle donnee."""
    if key_idx >= len(API_KEYS) or not API_KEYS[key_idx]:
        return False

    key = API_KEYS[key_idx]
    errors_count = KEY_STATE["errors"].get(key_idx, 0)

    # Si la cle a beaucoup d'erreurs 403, on utilise
    # seulement les modeles lite
    if errors_count > 3:
        models_to_try = ["gemini-2.5-flash-lite", "gemini-1.5-flash-latest"]
    else:
        models_to_try = MODELS_PRIORITY

    for model in models_to_try:
        url = ("https://generativelanguage.googleapis.com/v1beta/models/" +
               model + ":generateContent?key=" + key)

        # Payload simple sans options avancees pour le test
        payload = json.dumps({
            "contents": [{"parts": [{"text": "Reply with one word: READY"}]}],
            "generationConfig": {
                "maxOutputTokens": 20,
                "temperature": 0.0
            }
        }).encode()

        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                data = json.loads(r.read())
                text = extract_text_from_response(data)
                if text is not None:
                    print("[Gemini] Cle " + str(key_idx+1) +
                          " -> " + model + " OK")
                    ACTIVE_MODELS[key_idx] = {"model": model, "url": url}
                    return True
                else:
                    print("[Gemini] Cle " + str(key_idx+1) +
                          " " + model + ": reponse vide")
                    continue

        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print("[Gemini] Cle " + str(key_idx+1) +
                  " " + model + ": HTTP " + str(e.code))
            if e.code == 403:
                # Ce modele n'est pas dispo pour cette cle
                # Essayer le suivant
                time.sleep(0.5)
                continue
            elif e.code == 429:
                # Rate limit sur ce modele -> essayer le suivant
                time.sleep(2)
                continue
            elif e.code == 404:
                # Modele n'existe pas
                continue
            else:
                time.sleep(1)
                continue

        except Exception as e:
            print("[Gemini] Cle " + str(key_idx+1) +
                  " " + model + ": " + str(e))
            time.sleep(0.5)
            continue

    print("[Gemini] Cle " + str(key_idx+1) + ": aucun modele disponible")
    return False

def find_all_models():
    print("\n[Gemini] Initialisation " + str(len(API_KEYS)) + " cle(s)...")
    success = 0
    for i in range(len(API_KEYS)):
        if API_KEYS[i]:
            if find_model_for_key(i):
                success += 1
            else:
                time.sleep(2)
    print("[Gemini] " + str(success) + "/" + str(len(API_KEYS)) +
          " cle(s) OK")
    return success > 0

def gemini(prompt, max_tokens=65536, retries=3):
    if not ACTIVE_MODELS:
        if not find_all_models():
            return None

    if len(prompt) > 60000:
        prompt = prompt[:60000] + "\n...[TRONQUE]"

    payload_data = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.05,
        }
    }
    payload = json.dumps(payload_data).encode("utf-8")

    total_attempts = retries * max(len(API_KEYS), 1)

    for attempt in range(1, total_attempts + 1):
        key_idx = get_best_key()

        if key_idx not in ACTIVE_MODELS:
            if not find_model_for_key(key_idx):
                time.sleep(5)
                continue

        model_info = ACTIVE_MODELS[key_idx]
        key = API_KEYS[key_idx]
        url = model_info["url"].split("?")[0] + "?key=" + key

        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read().decode())
                text = extract_text_from_response(data)

                if text is None:
                    print("[Gemini] Cle " + str(key_idx+1) +
                          " reponse invalide, tentative " +
                          str(attempt) + "/" + str(total_attempts))
                    # Essayer un autre modele pour cette cle
                    if key_idx in ACTIVE_MODELS:
                        del ACTIVE_MODELS[key_idx]
                    find_model_for_key(key_idx)
                    continue

                finish = ""
                try:
                    finish = data["candidates"][0].get("finishReason", "STOP")
                except Exception:
                    pass

                print("[Gemini] Cle " + str(key_idx+1) + " -> " +
                      str(len(text)) + " chars (finish=" + finish + ")")
                return text

        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print("[Gemini] Cle " + str(key_idx+1) +
                  " HTTP " + str(e.code) +
                  " tentative " + str(attempt) + "/" + str(total_attempts))

            if e.code == 429:
                wait = min(60 + (30 * KEY_STATE["errors"].get(key_idx, 0)), 300)
                set_key_cooldown(key_idx, wait)
                if len(API_KEYS) > 1:
                    continue  # Rotation immediate
                time.sleep(min(wait, 60))

            elif e.code == 403:
                # Modele pas autorise sur cette cle
                # Essayer le modele suivant pour cette cle
                if key_idx in ACTIVE_MODELS:
                    del ACTIVE_MODELS[key_idx]
                if not find_model_for_key(key_idx):
                    set_key_cooldown(key_idx, 300)

            elif e.code in (400, 404):
                if key_idx in ACTIVE_MODELS:
                    del ACTIVE_MODELS[key_idx]
                find_model_for_key(key_idx)

            elif e.code == 500:
                time.sleep(30)

            else:
                time.sleep(20)

        except Exception as e:
            print("[Gemini] Cle " + str(key_idx+1) +
                  " Exception: " + str(e))
            time.sleep(15)

    print("[Gemini] ECHEC apres " + str(total_attempts) + " tentatives")
    return None

# ══════════════════════════════════════════════════════
# SOURCES
# ══════════════════════════════════════════════════════
def discover_files():
    found = []
    extensions = {".c", ".h", ".asm", ".ld", ".py"}
    exclude_dirs = {".git", "build", "__pycache__", ".github"}
    exclude_files = {"screen.h.save"}
    for root, dirs, files in os.walk(REPO_PATH):
        dirs[:] = [dd for dd in dirs if dd not in exclude_dirs]
        for f in files:
            if f in exclude_files:
                continue
            ext = os.path.splitext(f)[1]
            if ext in extensions or f == "Makefile":
                rel = os.path.relpath(
                    os.path.join(root, f), REPO_PATH
                ).replace("\\", "/")
                found.append(rel)
    return sorted(found)

def read_all():
    sources = {}
    all_files = list(set(ALL_FILES + discover_files()))
    for f in sorted(all_files):
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                sources[f] = fh.read()
        else:
            sources[f] = None
    return sources

def build_context(sources, max_chars=45000):
    ctx = "=== CODE SOURCE MAXOS ===\n\nFICHIERS:\n"
    for f, c in sources.items():
        ctx += "  " + ("[OK]" if c else "[MANQUANT]") + " " + f + "\n"
    ctx += "\n"
    chars_used = len(ctx)
    for f, c in sources.items():
        if c is None:
            continue
        block = ("=" * 60 + "\nFICHIER: " + f + "\n" +
                 "=" * 60 + "\n" + c + "\n\n")
        if chars_used + len(block) > max_chars:
            ctx += "[" + f + " tronque - trop grand]\n"
            continue
        ctx += block
        chars_used += len(block)
    return ctx

def get_project_stats(sources):
    total_lines = 0
    total_files = 0
    languages = {}
    for f, c in sources.items():
        if c:
            total_files += 1
            lines = c.count("\n")
            total_lines += lines
            ext = os.path.splitext(f)[1] or "Makefile"
            languages[ext] = languages.get(ext, 0) + lines
    return {"files": total_files, "lines": total_lines,
            "languages": languages}

# ══════════════════════════════════════════════════════
# GIT ET BUILD
# ══════════════════════════════════════════════════════
def git_cmd(args):
    r = subprocess.run(
        ["git"] + args, cwd=REPO_PATH,
        capture_output=True, text=True
    )
    return r.returncode == 0, r.stdout, r.stderr

def generate_commit_message(task_name, files_written, description, model_used):
    now = datetime.utcnow()
    dirs_touched = set()
    for f in files_written:
        if "/" in f:
            dirs_touched.add(f.split("/")[0])

    if "kernel" in dirs_touched:
        prefix = "kernel"
    elif "drivers" in dirs_touched:
        prefix = "driver"
    elif "boot" in dirs_touched:
        prefix = "boot"
    elif "ui" in dirs_touched:
        prefix = "ui"
    elif "apps" in dirs_touched:
        prefix = "feat(apps)"
    else:
        prefix = "feat"

    files_short = ", ".join([os.path.basename(f) for f in files_written[:4]])
    if len(files_written) > 4:
        files_short += " +" + str(len(files_written) - 4)

    short = prefix + ": " + task_name + " [" + files_short + "]"
    body = (
        "\n"
        "Component : " + ", ".join(sorted(dirs_touched)) + "\n"
        "Files     : " + ", ".join(files_written) + "\n"
        "Model     : " + model_used + "\n"
        "Timestamp : " + now.strftime("%Y-%m-%dT%H:%M:%SZ") + "\n"
        "\n"
        "Changes:\n"
        "  " + description[:200] + "\n"
        "\n"
        "Build: gcc -m32 -ffreestanding -nostdlib | nasm ELF32\n"
        "Target: x86 32-bit Protected Mode | QEMU i386\n"
    )
    return short, short + body

def git_push(task_name, files_written, description, model_used):
    if not files_written:
        return True, None, None
    short_msg, full_msg = generate_commit_message(
        task_name, files_written, description, model_used
    )
    git_cmd(["add", "-A"])
    ok, out, e = git_cmd(["commit", "-m", full_msg])
    if not ok:
        if "nothing to commit" in (out + e):
            print("[Git] Rien a committer")
            return True, None, None
        print("[Git] Commit KO: " + e[:200])
        return False, None, None

    _, sha, _ = git_cmd(["rev-parse", "HEAD"])
    sha = sha.strip()[:7]

    ok2, _, e2 = git_cmd(["push"])
    if not ok2:
        print("[Git] Push KO: " + e2[:200])
        return False, None, None

    print("[Git] OK " + sha + ": " + short_msg)
    return True, sha, short_msg

def make_build():
    subprocess.run(["make", "clean"], cwd=REPO_PATH, capture_output=True)
    r = subprocess.run(
        ["make"], cwd=REPO_PATH,
        capture_output=True, text=True, timeout=120
    )
    ok = r.returncode == 0
    log = r.stdout + r.stderr
    errors = []
    for line in log.split("\n"):
        if "error:" in line.lower():
            errors.append(line.strip())
    print("[Build] " + ("OK" if ok else "ECHEC") +
          " (" + str(len(errors)) + " erreurs)")
    if not ok:
        for e in errors[:6]:
            print("  -> " + e)
    return ok, log, errors[:15]

# ══════════════════════════════════════════════════════
# PARSER
# ══════════════════════════════════════════════════════
def parse_files(response):
    files = {}
    cur_file = None
    cur_lines = []
    in_file = False
    to_delete = []

    for line in response.split("\n"):
        s = line.strip()

        if "=== FILE:" in s and s.endswith("==="):
            try:
                start = s.index("=== FILE:") + 9
                end = s.rindex("===")
                fname = s[start:end].strip().strip("`").strip()
                if fname:
                    cur_file = fname
                    cur_lines = []
                    in_file = True
            except Exception:
                pass
            continue

        if s == "=== END FILE ===" and in_file:
            if cur_file:
                content = "\n".join(cur_lines).strip()
                for lang in ["```c", "```asm", "```nasm",
                             "```makefile", "```ld", "```bash", "```"]:
                    if content.startswith(lang):
                        content = content[len(lang):].lstrip("\n")
                        break
                if content.endswith("```"):
                    content = content[:-3].rstrip("\n")
                if content:
                    files[cur_file] = content
                    print("[Parse] OK " + cur_file +
                          " (" + str(len(content)) + " chars)")
            cur_file = None
            cur_lines = []
            in_file = False
            continue

        if "=== DELETE:" in s and s.endswith("==="):
            try:
                start = s.index("=== DELETE:") + 11
                end = s.rindex("===")
                fname = s[start:end].strip()
                if fname:
                    to_delete.append(fname)
                    print("[Parse] DELETE: " + fname)
            except Exception:
                pass
            continue

        if in_file:
            cur_lines.append(line)

    return files, to_delete

def write_files(files):
    written = []
    for path, content in files.items():
        if path.startswith("/") or ".." in path:
            continue
        full = os.path.join(REPO_PATH, path)
        parent = os.path.dirname(full)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        written.append(path)
        print("[Write] " + path + " (" + str(len(content)) + " chars)")
    return written

def delete_files(paths):
    deleted = []
    for path in paths:
        if path.startswith("/") or ".." in path:
            continue
        full = os.path.join(REPO_PATH, path)
        if os.path.exists(full):
            os.remove(full)
            deleted.append(path)
            print("[Delete] " + path)
    return deleted

def backup_files(paths):
    b = {}
    for p in paths:
        full = os.path.join(REPO_PATH, p)
        if os.path.exists(full):
            with open(full, "r", encoding="utf-8", errors="ignore") as f:
                b[p] = f.read()
    return b

def restore_files(backups):
    for p, c in backups.items():
        full = os.path.join(REPO_PATH, p)
        parent = os.path.dirname(full)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(c)
    print("[Restore] " + str(len(backups)) + " fichier(s)")

# ══════════════════════════════════════════════════════
# PHASE 1 : ANALYSE
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
        "Retourne UNIQUEMENT ce JSON valide, sans texte avant ni apres.\n"
        "Commence directement par { :\n\n"
        "{\n"
        '  "score_actuel": 35,\n'
        '  "niveau_os": "Prototype bare metal",\n'
        '  "commentaire_global": "Description courte",\n'
        '  "fonctionnalites_presentes": ["Boot x86", "VGA texte"],\n'
        '  "fonctionnalites_manquantes_critiques": ["IDT", "Timer PIT"],\n'
        '  "problemes_critiques": [\n'
        '    {"fichier": "kernel/kernel.c", "description": "probleme", "impact": "CRITIQUE"}\n'
        '  ],\n'
        '  "fichiers_obsoletes": [],\n'
        '  "plan_ameliorations": [\n'
        '    {\n'
        '      "nom": "IDT complete + PIC 8259",\n'
        '      "priorite": "CRITIQUE",\n'
        '      "categorie": "kernel",\n'
        '      "fichiers_a_modifier": ["kernel/kernel.c"],\n'
        '      "fichiers_a_creer": ["kernel/idt.h", "kernel/idt.c"],\n'
        '      "fichiers_a_supprimer": [],\n'
        '      "description": "Description technique preciseavec details implementati on",\n'
        '      "impact_attendu": "Ce que l utilisateur verra",\n'
        '      "complexite": "HAUTE"\n'
        '    }\n'
        '  ],\n'
        '  "prochaine_milestone": "Kernel stable"\n'
        "}"
    )

    response = gemini(prompt, max_tokens=4000)
    if not response:
        return None

    print("[Phase 1] " + str(len(response)) + " chars")

    clean = response.strip()
    if clean.startswith("```"):
        lines = clean.split("\n")[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        clean = "\n".join(lines).strip()

    # Nettoyer les backslashes invalides
    clean = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', clean)

    for attempt in range(3):
        i = clean.find("{")
        j = clean.rfind("}") + 1
        if i >= 0 and j > i:
            try:
                return json.loads(clean[i:j])
            except json.JSONDecodeError as e:
                print("[Phase 1] JSON err " + str(attempt+1) + ": " + str(e))

    # Plan par defaut
    print("[Phase 1] Plan par defaut")
    return {
        "score_actuel": 30,
        "niveau_os": "Prototype bare metal",
        "commentaire_global": "OS basique fonctionnel, base solide pour ameliorations",
        "fonctionnalites_presentes": [
            "Boot x86", "Mode texte VGA", "Clavier PS/2", "4 applications"
        ],
        "fonctionnalites_manquantes_critiques": [
            "IDT complete", "Timer PIT", "Gestionnaire memoire",
            "Mode graphique", "Systeme de fichiers"
        ],
        "problemes_critiques": [],
        "fichiers_obsoletes": [],
        "plan_ameliorations": [
            {
                "nom": "IDT 256 entrees + PIC 8259 + handlers exceptions x86",
                "priorite": "CRITIQUE",
                "categorie": "kernel",
                "fichiers_a_modifier": [
                    "kernel/kernel.c", "kernel/kernel_entry.asm"
                ],
                "fichiers_a_creer": ["kernel/idt.h", "kernel/idt.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "Implémenter IDT 256 entrées. Handlers pour exceptions "
                    "0-31 (div0, NMI, breakpoint, overflow, GPF, page fault). "
                    "Remapper PIC 8259 (IRQ0-7 -> INT 32-39, "
                    "IRQ8-15 -> INT 40-47). Stubs NASM pour chaque vecteur "
                    "avec save/restore registres. Handler generique affiche "
                    "nom exception + registres. Panic screen rouge."
                ),
                "impact_attendu": "OS stable, exceptions catchees, pas de triple fault",
                "complexite": "HAUTE"
            },
            {
                "nom": "Timer PIT 8253 100Hz + sleep_ms() + uptime",
                "priorite": "CRITIQUE",
                "categorie": "kernel",
                "fichiers_a_modifier": ["kernel/kernel.c"],
                "fichiers_a_creer": ["kernel/timer.h", "kernel/timer.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "Configurer PIT canal 0 a 100Hz (diviseur 11931). "
                    "Variable globale tick_count atomique. "
                    "timer_init(), timer_ticks(), sleep_ms(unsigned int ms). "
                    "Afficher uptime HH:MM:SS dans sysinfo. "
                    "Necessite IDT fonctionnelle pour IRQ0."
                ),
                "impact_attendu": "Horloge systeme, animations fluides, uptime dans sysinfo",
                "complexite": "MOYENNE"
            },
            {
                "nom": "Allocateur memoire physique bitmap pages 4KB",
                "priorite": "HAUTE",
                "categorie": "kernel",
                "fichiers_a_modifier": ["kernel/kernel.c"],
                "fichiers_a_creer": ["kernel/memory.h", "kernel/memory.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "Bitmap 1 bit par page 4KB. Zone utilisable 1MB-16MB "
                    "(3840 pages max). mem_init(), mem_alloc_page() -> addr, "
                    "mem_free_page(addr), mem_used_pages(), mem_free_pages(). "
                    "Afficher stats dans sysinfo: X MB libres / Y MB totaux."
                ),
                "impact_attendu": "Base pour allocation dynamique, stats memoire dans sysinfo",
                "complexite": "HAUTE"
            },
            {
                "nom": "Terminal 20 commandes + historique 20 entrees",
                "priorite": "HAUTE",
                "categorie": "app",
                "fichiers_a_modifier": [
                    "apps/terminal.h", "apps/terminal.c"
                ],
                "fichiers_a_creer": [],
                "fichiers_a_supprimer": [],
                "description": (
                    "Commandes: help, ver, mem, uptime, cls, echo [texte], "
                    "date, reboot, halt, color [fg] [bg], beep [freq] [dur], "
                    "calc [expr], snake, pong, about, credits, clear, ps, "
                    "sysinfo, license. "
                    "Historique circulaire 20 entrees (fleche haut/bas). "
                    "Prompt colore avec curseur clignotant. "
                    "Erreur si commande inconnue."
                ),
                "impact_attendu": "Terminal type cmd.exe, experience utilisateur amelioree",
                "complexite": "MOYENNE"
            },
            {
                "nom": "Desktop graphique VGA mode 13h 320x200",
                "priorite": "NORMALE",
                "categorie": "driver",
                "fichiers_a_modifier": [
                    "drivers/screen.h", "drivers/screen.c"
                ],
                "fichiers_a_creer": ["drivers/vga.h", "drivers/vga.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "Mode VGA 13h (320x200, 256 couleurs, framebuffer 0xA0000). "
                    "vga_init(), vga_pixel(x,y,col), vga_rect(x,y,w,h,col), "
                    "vga_hline(), vga_vline(), vga_clear(col), "
                    "vga_text(x,y,str,col). "
                    "Palette 256 couleurs standard VGA. "
                    "Desktop: fond degrade bleu-noir, barre taches bas, "
                    "icones applications. Fallback mode texte si echec init."
                ),
                "impact_attendu": "Interface graphique coloree type Windows 3.1",
                "complexite": "HAUTE"
            },
        ],
        "prochaine_milestone": "Kernel stable avec IDT + Timer + Memory"
    }

# ══════════════════════════════════════════════════════
# PHASE 2 : IMPLEMENTATION
# ══════════════════════════════════════════════════════
def phase_implement(task, all_sources):
    nom = task.get("nom", "Amelioration")
    categorie = task.get("categorie", "general")
    fichiers_m = task.get("fichiers_a_modifier", [])
    fichiers_c = task.get("fichiers_a_creer", [])
    fichiers_s = task.get("fichiers_a_supprimer", [])
    desc = task.get("description", "")
    impact = task.get("impact_attendu", "")
    complexite = task.get("complexite", "MOYENNE")
    tous = list(set(fichiers_m + fichiers_c))

    current_model = ACTIVE_MODELS.get(
        KEY_STATE["current_index"], {}
    ).get("model", "gemini")

    print("\n[Impl] " + nom)
    print("  Cat: " + categorie + " | Complexite: " + complexite)
    print("  Modifier:  " + str(fichiers_m))
    print("  Creer:     " + str(fichiers_c))
    print("  Supprimer: " + str(fichiers_s))

    # Construire le contexte cible
    lies = set(tous)
    for f in tous:
        base = f.replace(".c", "").replace(".h", "")
        for ext in [".c", ".h"]:
            if (base + ext) in all_sources:
                lies.add(base + ext)

    # Toujours inclure les fichiers cles
    for key in ["kernel/kernel.c", "drivers/screen.h",
                "drivers/keyboard.h", "ui/ui.h", "ui/ui.c",
                "Makefile", "linker.ld", "kernel/kernel_entry.asm"]:
        lies.add(key)

    ctx = "=== FICHIERS CONCERNES ===\n\n"
    for f in sorted(lies):
        c = all_sources.get(f, "")
        ctx += "--- " + f + " ---\n"
        ctx += (c if c else "[MANQUANT - A CREER]") + "\n\n"

    prompt = (
        "Tu es un expert OS bare metal x86.\n"
        "Tu developpes MaxOS avec l'ambition d'un OS complet.\n\n" +
        BARE_METAL_RULES + "\n\n" +
        OS_MISSION + "\n\n" +
        ctx + "\n"
        "TACHE : " + nom + "\n"
        "CATEGORIE : " + categorie + "\n"
        "COMPLEXITE : " + complexite + "\n"
        "DESCRIPTION : " + desc + "\n"
        "IMPACT ATTENDU : " + impact + "\n"
        "FICHIERS A MODIFIER : " + str(fichiers_m) + "\n"
        "FICHIERS A CREER : " + str(fichiers_c) + "\n"
        "FICHIERS A SUPPRIMER : " + str(fichiers_s) + "\n\n"
        "INSTRUCTIONS :\n"
        "1. Code COMPLET dans chaque fichier\n"
        "2. JAMAIS de '// reste inchange' ou '...'\n"
        "3. Nouveaux .c -> mettre a jour Makefile\n"
        "4. Pour supprimer un fichier: === DELETE: chemin ===\n"
        "5. Commenter avec /* */ les sections importantes\n"
        "6. Tester mentalement que le code compile\n\n"
        "FORMAT OBLIGATOIRE:\n"
        "=== FILE: chemin/fichier.c ===\n"
        "[code complet]\n"
        "=== END FILE ===\n\n"
        "COMMENCE DIRECTEMENT PAR LE PREMIER FICHIER :"
    )

    t0 = time.time()
    max_tok = 65536 if complexite == "HAUTE" else 32768
    response = gemini(prompt, max_tokens=max_tok)
    elapsed = time.time() - t0

    if not response:
        d("Echec: " + nom, "Gemini n'a pas repondu.", 0xFF0000)
        return False, [], []

    print("[Impl] " + str(len(response)) +
          " chars en " + str(round(elapsed, 1)) + "s")

    files, to_delete = parse_files(response)

    if not files and not to_delete:
        print("[Debug] Debut reponse:\n" + response[:500])
        d("Echec parse: " + nom,
          "Aucun fichier parse.\n```\n" + response[:400] + "\n```",
          0xFF0000)
        return False, [], []

    backs = backup_files(list(files.keys()))
    written = write_files(files)
    deleted = delete_files(to_delete)

    if not written and not deleted:
        d("Echec: " + nom, "Aucun fichier ecrit", 0xFF0000)
        return False, [], []

    build_ok, log, errors = make_build()

    if build_ok:
        pushed, sha, short_msg = git_push(
            nom, written + deleted, desc, current_model
        )
        if pushed:
            return True, written, deleted
        restore_files(backs)
        return False, [], []
    else:
        fixed = auto_fix(log, errors, files, backs, current_model)
        if fixed:
            return True, written, deleted
        restore_files(backs)
        for p in written:
            if p not in backs:
                fp = os.path.join(REPO_PATH, p)
                if os.path.exists(fp):
                    os.remove(fp)
        return False, [], []

# ══════════════════════════════════════════════════════
# AUTO-FIX
# ══════════════════════════════════════════════════════
def auto_fix(build_log, errors, generated_files, backups,
             model_used, max_attempts=2):
    print("[Fix] Correction automatique...")

    for attempt in range(1, max_attempts + 1):
        print("[Fix] Tentative " + str(attempt) + "/" + str(max_attempts))

        current = {}
        for p in generated_files:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp):
                with open(fp, "r") as f:
                    current[p] = f.read()

        ctx = ""
        for p, c in current.items():
            ctx += "--- " + p + " ---\n" + c[:3000] + "\n\n"

        error_txt = "\n".join(errors[:12])

        prompt = (
            "Corrige ces erreurs de compilation bare metal x86.\n\n" +
            BARE_METAL_RULES + "\n\n"
            "ERREURS:\n```\n" + error_txt + "\n```\n\n"
            "LOG FIN:\n```\n" + build_log[-1500:] + "\n```\n\n"
            "FICHIERS ACTUELS:\n" + ctx + "\n"
            "REGLES: Code complet, pas de librairies standard.\n\n"
            "=== FILE: fichier.c ===\n"
            "[code corrige complet]\n"
            "=== END FILE ==="
        )

        response = gemini(prompt, max_tokens=32768)
        if not response:
            continue

        files, _ = parse_files(response)
        if not files:
            continue

        write_files(files)
        ok, log, new_errors = make_build()

        if ok:
            git_push(
                "fix: correction erreurs compilation",
                list(files.keys()),
                "Auto-fix: " + str(len(errors)) + " erreurs -> 0",
                model_used
            )
            d("Auto-correction reussie",
              "Tentative " + str(attempt) + ": " +
              str(len(errors)) + " erreurs corrigees.",
              0x00AAFF)
            return True

        errors = new_errors
        time.sleep(10)

    restore_files(backups)
    return False

# ══════════════════════════════════════════════════════
# GESTION PULL REQUESTS
# ══════════════════════════════════════════════════════
def handle_pull_requests():
    prs = github_get_open_prs()
    if not prs:
        print("[PR] Aucune PR ouverte")
        return

    print("[PR] " + str(len(prs)) + " PR(s)")

    for pr in prs:
        pr_number = pr.get("number")
        pr_title = pr.get("title", "")
        pr_author = pr.get("user", {}).get("login", "unknown")
        pr_body = pr.get("body", "") or ""

        # Ne pas auto-merger les PRs faites par l'IA elle-meme
        if "AI" in pr_author or pr_author == "github-actions":
            print("[PR] Skip PR bot: #" + str(pr_number))
            continue

        print("[PR] Analyse #" + str(pr_number) + ": " + pr_title)

        files_data = github_api(
            "GET", "pulls/" + str(pr_number) + "/files"
        )
        if not files_data:
            continue

        file_list = "\n".join([
            "- " + f.get("filename", "?") +
            " (+" + str(f.get("additions", 0)) +
            " -" + str(f.get("deletions", 0)) + ")"
            for f in files_data[:15]
        ])

        patches = ""
        for f in files_data[:3]:
            patch = f.get("patch", "")[:600]
            if patch:
                patches += "--- " + f.get("filename", "?") + " ---\n"
                patches += patch + "\n\n"

        prompt = (
            "Tu es le mainteneur de MaxOS (OS bare metal x86).\n\n" +
            BARE_METAL_RULES + "\n\n"
            "PR #" + str(pr_number) + ": " + pr_title + "\n"
            "Auteur: " + pr_author + "\n"
            "Description: " + pr_body[:300] + "\n\n"
            "Fichiers:\n" + file_list + "\n\n"
            "Changements:\n" + patches + "\n\n"
            "Reponds en JSON simple:\n"
            "{\n"
            '  "action": "MERGE" ou "REJECT",\n'
            '  "raison": "courte",\n'
            '  "commentaire": "pour le dev"\n'
            "}\n\n"
            "MERGER si: compile, bare metal, ameliore l OS.\n"
            "REJETER si: librairies standard, casse le build.\n"
            "Commence par { :"
        )

        response = gemini(prompt, max_tokens=500)
        if not response:
            continue

        action = "REJECT"
        raison = "Analyse impossible"
        commentaire = "Review automatique echouee"

        try:
            clean = response.strip()
            if clean.startswith("```"):
                lines = clean.split("\n")[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                clean = "\n".join(lines)
            i = clean.find("{")
            j = clean.rfind("}") + 1
            if i >= 0 and j > i:
                dec = json.loads(clean[i:j])
                action = dec.get("action", "REJECT")
                raison = dec.get("raison", "")
                commentaire = dec.get("commentaire", "")
        except Exception:
            pass

        comment_body = (
            "## Review automatique MaxOS AI v8.1\n\n"
            "**Decision:** " + action + "\n"
            "**Raison:** " + raison + "\n\n"
            + commentaire + "\n\n"
            "---\n*Review par MaxOS AI Developer v8.1*"
        )

        github_comment_pr(pr_number, comment_body)

        if action == "MERGE":
            if github_merge_pr(pr_number, pr_title):
                d("PR #" + str(pr_number) + " mergee",
                  pr_title + "\n" + raison, 0x00FF88)
            else:
                print("[PR] Merge echec #" + str(pr_number))
        else:
            github_close_pr(pr_number)
            d("PR #" + str(pr_number) + " rejetee",
              pr_title + "\n" + raison, 0xFF4444)

# ══════════════════════════════════════════════════════
# RELEASE
# ══════════════════════════════════════════════════════
def create_release(tasks_done, tasks_failed, analyse_data, stats):
    if not GITHUB_TOKEN:
        return None

    result = github_api("GET", "tags?per_page=1")
    last_tag = "v0.0.0"
    if result and len(result) > 0:
        last_tag = result[0].get("name", "v0.0.0")

    try:
        parts = [int(x) for x in last_tag.lstrip("v").split(".")]
        if len(tasks_done) >= 3:
            parts[1] += 1
            parts[2] = 0
        else:
            parts[2] += 1
        new_tag = ("v" + str(parts[0]) + "." +
                   str(parts[1]) + "." + str(parts[2]))
    except Exception:
        new_tag = "v1.0.0"

    now = datetime.utcnow()
    score = analyse_data.get("score_actuel", 0)
    niveau = analyse_data.get("niveau_os", "Prototype")
    milestone = analyse_data.get("prochaine_milestone", "")
    features = analyse_data.get("fonctionnalites_presentes", [])

    changes_md = ""
    for t in tasks_done:
        nom = t.get("nom", "?")
        files = t.get("files", [])
        sha = t.get("sha", "")
        model = t.get("model", "")
        sha_link = ""
        if sha:
            sha_link = (" [`" + sha + "`](https://github.com/" +
                       REPO_OWNER + "/" + REPO_NAME + "/commit/" + sha + ")")
        changes_md += "- **" + nom + "**" + sha_link + "\n"
        if files:
            changes_md += "  - `" + "`, `".join(files[:5]) + "`\n"
        if model:
            changes_md += "  - Modele: `" + model + "`\n"

    failed_md = "".join(["- ~~" + t + "~~\n" for t in tasks_failed])

    features_md = "\n".join(["  - " + f for f in features])

    models_used = ", ".join([
        ACTIVE_MODELS.get(i, {}).get("model", "?")
        for i in range(len(API_KEYS)) if i in ACTIVE_MODELS
    ])

    body = (
        "# MaxOS " + new_tag + "\n\n"
        "> Release generee automatiquement par MaxOS AI Developer v8.1\n"
        "> Objectif: OS complet a l'echelle de Windows 11\n\n"
        "---\n\n"
        "## Etat du projet\n\n"
        "| Metrique | Valeur |\n|---|---|\n"
        "| Score | " + str(score) + "/100 |\n"
        "| Niveau | " + niveau + " |\n"
        "| Fichiers | " + str(stats.get("files", 0)) + " |\n"
        "| Lignes | " + str(stats.get("lines", 0)) + " |\n"
        "| Milestone | " + milestone + " |\n\n"
        "---\n\n"
        "## Changements\n\n" +
        (changes_md or "- Maintenance\n") +
        ("\n## Reporte\n\n" + failed_md if failed_md else "") +
        "\n---\n\n"
        "## Fonctionnalites\n\n" + features_md + "\n\n"
        "---\n\n"
        "## Tester MaxOS\n\n"
        "### Telecharger os.img\n\n"
        "```\n"
        "GitHub -> Actions -> Dernier run reussi\n"
        "-> Artifacts -> maxos-build-XXX -> Telecharger\n"
        "```\n\n"
        "### Lancer avec QEMU\n\n"
        "**Linux / WSL Ubuntu:**\n"
        "```bash\n"
        "sudo apt install qemu-system-x86\n"
        "qemu-system-i386 -drive format=raw,file=os.img,"
        "if=floppy -boot a -vga std -k fr -m 32 -no-reboot\n"
        "```\n\n"
        "**Windows (QEMU installe):**\n"
        "```\n"
        "# Installer QEMU: https://www.qemu.org/windows/\n"
        "# Dans PowerShell (adapter le chemin QEMU):\n"
        'C:\\Program Files\\qemu\\qemu-system-i386.exe '
        '-drive format=raw,file=os.img,if=floppy '
        '-boot a -vga std -k fr -m 32\n'
        "```\n\n"
        "**Compiler depuis les sources (WSL):**\n"
        "```bash\n"
        "sudo apt install nasm gcc make gcc-multilib qemu-system-x86\n"
        "git clone https://github.com/" + REPO_OWNER + "/" + REPO_NAME + "\n"
        "cd MaxOS && make && make run\n"
        "```\n\n"
        "---\n\n"
        "## Controles\n\n"
        "| Touche | Action |\n|---|---|\n"
        "| TAB | Changer d'application |\n"
        "| F1 | Bloc-Notes |\n"
        "| F2 | Terminal |\n"
        "| F3 | Informations systeme |\n"
        "| F4 | A propos |\n\n"
        "---\n\n"
        "## Technique\n\n"
        "| Composant | Detail |\n|---|---|\n"
        "| Architecture | x86 32-bit Protected Mode |\n"
        "| Compilateur | GCC -m32 -ffreestanding -nostdlib |\n"
        "| Assembleur | NASM ELF32 |\n"
        "| Linker | GNU LD script custom |\n"
        "| Emulateur | QEMU i386 |\n"
        "| IA | " + models_used + " |\n\n"
        "## Roadmap\n\n"
        "| Phase | Statut | Objectif |\n|---|---|---|\n"
        "| 1 | En cours | IDT + Timer + Memoire |\n"
        "| 2 | Planifie | Mode graphique VESA |\n"
        "| 3 | Planifie | Systeme fichiers FAT12 |\n"
        "| 4 | Planifie | GUI fenetres + souris |\n"
        "| 5 | Planifie | Applications avancees |\n"
        "| 6 | Futur | Reseau TCP/IP |\n\n"
        "---\n"
        "*MaxOS AI v8.1 | " + now.strftime("%Y-%m-%d %H:%M") + " UTC*\n"
    )

    url = github_create_release(
        tag=new_tag,
        name="MaxOS " + new_tag + " - " + niveau + " | " +
             now.strftime("%Y-%m-%d"),
        body=body,
        prerelease=(score < 50)
    )

    if url:
        d(
            "Release " + new_tag + " publiee",
            "Niveau: " + niveau + "\nScore: " + str(score) + "/100",
            0x00FF88,
            [
                {"name": "Version",   "value": new_tag,
                 "inline": True},
                {"name": "Score",     "value": str(score) + "/100",
                 "inline": True},
                {"name": "Succes",    "value": str(len(tasks_done)),
                 "inline": True},
                {"name": "Lien",
                 "value": "[Release](" + url + ")",
                 "inline": False},
            ]
        )
    return url

# ══════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("  MaxOS AI Developer v8.1")
    print("  Objectif: OS echelle Windows 11")
    print("  Mode: Autonome 24/7 | Multi-cles | Auto PR+Release")
    print("=" * 60 + "\n")

    if not find_all_models():
        print("FATAL: Aucune cle Gemini operationnelle")
        sys.exit(1)

    d(
        "MaxOS AI Developer v8.1 demarre",
        ("Objectif: OS echelle Windows 11\n"
         "Cles actives: " + str(len(ACTIVE_MODELS)) +
         "/" + str(len(API_KEYS))),
        0x5865F2,
        [
            {"name": "Modeles actifs",
             "value": "\n".join([
                 "Cle " + str(i+1) + ": " + ACTIVE_MODELS[i]["model"]
                 for i in sorted(ACTIVE_MODELS.keys())
             ]) or "Aucun",
             "inline": False},
            {"name": "Repo",
             "value": REPO_OWNER + "/" + REPO_NAME,
             "inline": True},
            {"name": "Heure UTC",
             "value": datetime.utcnow().strftime("%H:%M:%S"),
             "inline": True},
        ]
    )

    # Gestion PRs
    print("\n[PRs] Verification...")
    handle_pull_requests()

    # Sources
    sources = read_all()
    context = build_context(sources)
    stats = get_project_stats(sources)
    print("[Sources] " + str(stats["files"]) + " fichiers, " +
          str(stats["lines"]) + " lignes")

    # Phase 1
    print("\n" + "="*60)
    print(" PHASE 1 : Analyse")
    print("="*60)

    analyse = phase_analyse(context, stats)
    if not analyse:
        d("Analyse echouee", "Impossible d'analyser.", 0xFF0000)
        sys.exit(1)

    score = analyse.get("score_actuel", 0)
    niveau = analyse.get("niveau_os", "?")
    plan = analyse.get("plan_ameliorations", [])
    milestone = analyse.get("prochaine_milestone", "?")
    features = analyse.get("fonctionnalites_presentes", [])
    manquantes = analyse.get("fonctionnalites_manquantes_critiques", [])

    print("[Rapport] Score: " + str(score) + "/100")
    print("[Rapport] Niveau: " + niveau)
    print("[Rapport] " + str(len(plan)) + " taches")

    features_txt = "\n".join(["+ " + f for f in features[:5]]) or "Aucune"
    manquantes_txt = "\n".join(["- " + f for f in manquantes[:5]]) or "Aucune"
    plan_txt = "\n".join([
        "[" + str(i+1) + "] [" + t.get("priorite", "?") + "] " +
        t.get("nom", "?")
        for i, t in enumerate(plan[:6])
    ])

    d(
        "Rapport - Score " + str(score) + "/100",
        "```\n" + progress_bar(score) + "\n```\nNiveau: " + niveau,
        0x00AAFF if score >= 60 else 0xFFA500 if score >= 30 else 0xFF4444,
        [
            {"name": "Presentes",   "value": features_txt[:400],  "inline": True},
            {"name": "Manquantes",  "value": manquantes_txt[:400], "inline": True},
            {"name": "Plan",
             "value": "```\n" + plan_txt + "\n```", "inline": False},
            {"name": "Milestone",   "value": milestone[:80], "inline": False},
            {"name": "Cles",        "value": key_status_str(), "inline": False},
        ]
    )

    # Phase 2
    print("\n" + "="*60)
    print(" PHASE 2 : Implementation")
    print("="*60)

    order = {"CRITIQUE": 0, "HAUTE": 1, "NORMALE": 2, "BASSE": 3}
    plan_sorted = sorted(
        plan,
        key=lambda x: order.get(x.get("priorite", "NORMALE"), 2)
    )

    success = 0
    total = len(plan_sorted)
    tasks_done = []
    tasks_failed = []

    for i, task in enumerate(plan_sorted, 1):
        nom = task.get("nom", "Tache " + str(i))
        priorite = task.get("priorite", "NORMALE")
        categorie = task.get("categorie", "?")

        print("\n" + "="*60)
        print(" [" + str(i) + "/" + str(total) + "] " +
              "[" + priorite + "] " + nom)
        print("="*60)

        current_model = ACTIVE_MODELS.get(
            KEY_STATE["current_index"], {}
        ).get("model", "?")

        d(
            "[" + str(i) + "/" + str(total) + "] " + nom,
            ("```\n" + progress_bar(int((i-1)/total*100)) + "\n```\n" +
             task.get("description", "")[:200]),
            0xFFA500,
            [
                {"name": "Priorite",  "value": priorite,      "inline": True},
                {"name": "Categorie", "value": categorie,     "inline": True},
                {"name": "Modele",    "value": current_model, "inline": True},
            ]
        )

        sources = read_all()
        ok, written, deleted = phase_implement(task, sources)

        _, latest_sha, _ = git_cmd(["rev-parse", "HEAD"])
        latest_sha = latest_sha.strip()[:7] if latest_sha.strip() else "?"

        if ok:
            success += 1
            tasks_done.append({
                "nom": nom,
                "files": written + deleted,
                "sha": latest_sha,
                "model": current_model,
            })
            d(
                "Succes: " + nom,
                "Commit: `" + latest_sha + "`",
                0x00FF88,
                [
                    {"name": "Ecrits",
                     "value": "\n".join(["`" + f + "`"
                                        for f in written[:5]]) or "Aucun",
                     "inline": True},
                    {"name": "Supprimes",
                     "value": "\n".join(["`" + f + "`"
                                        for f in deleted]) or "Aucun",
                     "inline": True},
                ]
            )
            sources = read_all()
        else:
            tasks_failed.append(nom)
            d("Echec: " + nom,
              "Code restaure. Reporte.", 0xFF6600)

        if i < total:
            pause = 10 if len(API_KEYS) > 1 else 20
            print("[Pause] " + str(pause) + "s...")
            time.sleep(pause)

    # Release
    if success > 0:
        print("\n[Release] Creation...")
        sources = read_all()
        stats = get_project_stats(sources)
        create_release(tasks_done, tasks_failed, analyse, stats)

    # Rapport final
    pct = int(success / total * 100) if total > 0 else 0
    color = (0x00FF88 if pct >= 80 else
             0xFFA500 if pct >= 50 else 0xFF4444)

    d(
        "Cycle termine - " + str(success) + "/" + str(total),
        "```\n" + progress_bar(pct) + "\n```",
        color,
        [
            {"name": "Succes",  "value": str(success),       "inline": True},
            {"name": "Echecs",  "value": str(total-success), "inline": True},
            {"name": "Taux",    "value": str(pct) + "%",     "inline": True},
            {"name": "Cles",    "value": key_status_str(),   "inline": False},
        ]
    )

    print("\n[FIN] " + str(success) + "/" + str(total))

if __name__ == "__main__":
    main()
