#!/usr/bin/env python3
"""MaxOS AI Developer v8.0 - Multi-Key + Autonomous 24/7"""

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

API_KEYS        = load_api_keys()
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")
GITHUB_TOKEN    = os.environ.get("GITHUB_TOKEN", "")
REPO_OWNER      = os.environ.get("REPO_OWNER", "MaxLananas")
REPO_NAME       = os.environ.get("REPO_NAME", "MaxOS")
REPO_PATH       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KEY_STATE = {
    "current_index": 0,
    "cooldowns":     {},
    "usage_count":   {},
    "errors":        {},
}

def mask_key(k):
    if len(k) > 8:
        return k[:4] + "*" * max(0, len(k) - 8) + k[-4:]
    return "***"

print("[Config] Cles Gemini : " + str(len(API_KEYS)) + " cle(s) chargee(s)")
for i, k in enumerate(API_KEYS):
    print("         Cle " + str(i+1) + "      : " + mask_key(k))
print("[Config] Discord     : " + ("OK" if DISCORD_WEBHOOK else "ABSENT"))
print("[Config] GitHub      : " + ("OK" if GITHUB_TOKEN else "ABSENT"))
print("[Config] Repo        : " + REPO_OWNER + "/" + REPO_NAME)
print("[Config] Path        : " + REPO_PATH)

if not API_KEYS:
    print("FATAL: Aucune GEMINI_API_KEY trouvee")
    sys.exit(1)

# ══════════════════════════════════════════════════════
# MODELES GEMINI
# ══════════════════════════════════════════════════════
MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

ACTIVE_MODELS = {}

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
# MISSION - OBJECTIF WINDOWS 11
# ══════════════════════════════════════════════════════
OS_MISSION = """
MISSION MAXOS - OBJECTIF WINDOWS 11 SCALE

MaxOS a pour ambition de devenir un OS complet.
L'IA est le developpeur principal, autonome, 24h/24 7j/7.
L'IA peut creer, supprimer et modifier n'importe quel fichier.

FONCTIONNALITES A IMPLEMENTER PAR ORDRE DE PRIORITE :

COUCHE 1 - FONDATIONS :
  - Gestionnaire de memoire (paging, bitmap allocator)
  - GDT/IDT robustes avec tous les handlers d'exceptions x86
  - Timer PIT 8253 (100Hz, sleep, uptime)
  - Interruptions hardware completes (IRQ 0-15)
  - Pile d'appels systeme

COUCHE 2 - DRIVERS :
  - Driver clavier PS/2 complet (toutes touches, Shift, Ctrl, Alt)
  - Driver VGA texte 80x25 avec 16 couleurs
  - Driver VGA graphique mode 13h (320x200, 256 couleurs)
  - Driver serie COM1 (debug)
  - Driver son PC speaker (beeps, mélodies)
  - Driver souris PS/2

COUCHE 3 - SYSTEME DE FICHIERS :
  - FAT12 sur disquette (lecture/ecriture)
  - VFS abstrait
  - Repertoires et fichiers

COUCHE 4 - INTERFACE GRAPHIQUE :
  - Fenetres avec barres de titre, bordures, boutons
  - Z-order (fenetres empilees)
  - Curseur souris PS/2
  - Desktop avec fond d'ecran
  - Taskbar style Windows 11
  - Menu demarrer
  - Animations

COUCHE 5 - APPLICATIONS :
  - Explorateur de fichiers
  - Editeur de texte avance
  - Terminal puissant (20+ commandes)
  - Gestionnaire des taches
  - Calculatrice
  - Horloge/Calendrier
  - Jeux (Snake, Tetris, Pong)
  - Editeur hexadecimal
  - Lecteur musique PC speaker

COUCHE 6 - RESEAU :
  - Driver NE2000
  - Stack TCP/IP minimale
  - DHCP client

REGLES IMPORTANTES :
- Chaque amelioration doit compiler et booter dans QEMU
- Code C pure bare metal : ZERO librairie standard
- L'IA peut creer, supprimer et modifier n'importe quel fichier
- Preferer la stabilite a la complexite
- Mettre a jour le Makefile quand on cree de nouveaux .c
"""

BARE_METAL_RULES = """
REGLES ABSOLUES BARE METAL x86 (VIOLATION = ECHEC DE COMPILATION) :

1. ZERO include de librairie standard :
   PAS #include <stddef.h>, <string.h>, <stdlib.h>, <stdio.h>,
       <stdint.h>, <stdbool.h>

2. ZERO types de librairie :
   PAS size_t  -> utilise unsigned int
   PAS NULL    -> utilise 0
   PAS bool    -> utilise int
   PAS true/false -> utilise 1/0
   PAS uint32_t -> utilise unsigned int

3. ZERO fonctions de librairie :
   PAS malloc/free, memset/memcpy, strlen/strcmp, printf/sprintf

4. FONCTIONS EXISTANTES A RESPECTER :
   - nb_init(), nb_draw(), nb_key(char k) -> notepad
   - tm_init(), tm_draw(), tm_key(char k) -> terminal
   - si_draw() -> sysinfo (PAS si_init, PAS si_key)
   - ab_draw() -> about   (PAS ab_init, PAS ab_key)
   - kb_init(), kb_haskey(), kb_getchar() -> keyboard
   - v_init(), v_put(), v_str(), v_fill() -> screen

5. COMPILATION :
   gcc -m32 -ffreestanding -fno-stack-protector -fno-builtin
       -fno-pic -fno-pie -nostdlib -nostdinc -w -c
   nasm -f elf (pour .o) / nasm -f bin (pour boot.bin)
   ld -m elf_i386 -T linker.ld --oformat binary

6. L'IA PEUT ET DOIT :
   - Creer de nouveaux fichiers .c/.h/.asm si necessaire
   - Supprimer des fichiers obsoletes
   - Mettre a jour le Makefile pour integrer nouveaux fichiers
   - Restructurer le projet si necessaire
"""

# ══════════════════════════════════════════════════════
# ROTATION DES CLES
# ══════════════════════════════════════════════════════
def get_best_key():
    now = time.time()
    n = len(API_KEYS)
    for attempt in range(n):
        idx = (KEY_STATE["current_index"] + attempt) % n
        cooldown_end = KEY_STATE["cooldowns"].get(idx, 0)
        if now >= cooldown_end:
            KEY_STATE["current_index"] = idx
            KEY_STATE["usage_count"][idx] = KEY_STATE["usage_count"].get(idx, 0) + 1
            return idx
    min_idx = min(range(n), key=lambda i: KEY_STATE["cooldowns"].get(i, 0))
    wait = KEY_STATE["cooldowns"].get(min_idx, 0) - now + 1
    print("[Keys] Toutes les cles en cooldown. Attente " + str(int(wait)) + "s")
    time.sleep(max(wait, 1))
    return min_idx

def set_key_cooldown(key_idx, seconds):
    KEY_STATE["cooldowns"][key_idx] = time.time() + seconds
    KEY_STATE["errors"][key_idx] = KEY_STATE["errors"].get(key_idx, 0) + 1
    n = len(API_KEYS)
    if n > 1:
        next_idx = (key_idx + 1) % n
        KEY_STATE["current_index"] = next_idx
        print("[Keys] Cle " + str(key_idx+1) + " cooldown " + str(seconds) +
              "s -> bascule cle " + str(next_idx+1))
    else:
        print("[Keys] Cle unique cooldown " + str(seconds) + "s")

def key_status_str():
    now = time.time()
    lines = []
    for i in range(len(API_KEYS)):
        cd = KEY_STATE["cooldowns"].get(i, 0)
        usage = KEY_STATE["usage_count"].get(i, 0)
        errors = KEY_STATE["errors"].get(i, 0)
        status = "OK" if now >= cd else "CD " + str(int(cd - now)) + "s"
        model = ACTIVE_MODELS.get(i, {}).get("model", "?")
        lines.append("Cle " + str(i+1) + ": " + status +
                     " | " + str(usage) + " req | " + model)
    return "\n".join(lines)

# ══════════════════════════════════════════════════════
# GITHUB API
# ══════════════════════════════════════════════════════
def github_api(method, endpoint, data=None):
    if not GITHUB_TOKEN:
        return None
    url = ("https://api.github.com/repos/" + REPO_OWNER + "/" +
           REPO_NAME + "/" + endpoint)
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
              " -> HTTP " + str(e.code) + ": " + body[:200])
        return None
    except Exception as e:
        print("[GitHub] Erreur: " + str(e))
        return None

def github_create_release(tag, name, body, prerelease=False):
    data = {
        "tag_name": tag,
        "name": name,
        "body": body,
        "draft": False,
        "prerelease": prerelease,
        "generate_release_notes": False,
    }
    result = github_api("POST", "releases", data)
    if result and "html_url" in result:
        print("[GitHub] Release creee: " + result["html_url"])
        return result["html_url"]
    return None

def github_get_open_prs():
    result = github_api("GET", "pulls?state=open&per_page=10")
    return result if isinstance(result, list) else []

def github_merge_pr(pr_number, title):
    data = {
        "commit_title": "merge: " + title + " [AI auto-merge]",
        "merge_method": "squash"
    }
    result = github_api("PUT", "pulls/" + str(pr_number) + "/merge", data)
    if result and result.get("merged"):
        print("[GitHub] PR #" + str(pr_number) + " mergee")
        return True
    return False

def github_comment_pr(pr_number, body):
    github_api("POST", "issues/" + str(pr_number) + "/comments", {"body": body})

def github_close_pr(pr_number, reason):
    github_comment_pr(pr_number, reason)
    github_api("PATCH", "pulls/" + str(pr_number), {"state": "closed"})

def github_create_issue(title, body, labels=None):
    data = {"title": title, "body": body, "labels": labels or []}
    result = github_api("POST", "issues", data)
    if result and "html_url" in result:
        return result.get("number"), result["html_url"]
    return None, None

def github_close_issue(issue_number):
    github_api("PATCH", "issues/" + str(issue_number), {"state": "closed"})

def github_get_stats():
    repo = github_api("GET", "")
    commits = github_api("GET", "commits?per_page=5")
    return repo, commits

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
        with urllib.request.urlopen(req, timeout=15) as r:
            return True
    except Exception as e:
        print("[Discord] Err: " + str(e))
    return False

def make_embed(title, desc, color, fields=None):
    active_keys = sum(1 for i in range(len(API_KEYS))
                      if time.time() >= KEY_STATE["cooldowns"].get(i, 0))
    current_model = ACTIVE_MODELS.get(
        KEY_STATE["current_index"], {}
    ).get("model", "init")
    e = {
        "title": str(title)[:256],
        "description": str(desc)[:4096],
        "color": color,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "footer": {
            "text": ("MaxOS AI v8.0  |  " + current_model +
                     "  |  " + str(active_keys) + "/" + str(len(API_KEYS)) +
                     " cles  |  " + REPO_OWNER + "/" + REPO_NAME),
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
# GEMINI AVEC ROTATION
# ══════════════════════════════════════════════════════
def find_model_for_key(key_idx):
    if key_idx >= len(API_KEYS) or not API_KEYS[key_idx]:
        return False
    key = API_KEYS[key_idx]
    for model in MODELS:
        url = ("https://generativelanguage.googleapis.com/v1beta/models/" +
               model + ":generateContent?key=" + key)
        payload = json.dumps({
            "contents": [{"parts": [{"text": "Reply: READY"}]}],
            "generationConfig": {"maxOutputTokens": 10}
        }).encode()
        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read())
                txt = data["candidates"][0]["content"]["parts"][0]["text"]
                print("[Gemini] Cle " + str(key_idx+1) +
                      " -> " + model + " OK")
                ACTIVE_MODELS[key_idx] = {"model": model, "url": url}
                return True
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print("[Gemini] Cle " + str(key_idx+1) +
                  " " + model + ": HTTP " + str(e.code))
            if e.code == 403:
                try:
                    msg = json.loads(body).get("error", {}).get("message", "")
                    if "leaked" in msg.lower():
                        print("ALERTE: Cle " + str(key_idx+1) + " compromise!")
                        d("ALERTE SECURITE",
                          "Cle " + str(key_idx+1) + " Gemini compromise!",
                          0xFF0000)
                        API_KEYS[key_idx] = ""
                        return False
                except Exception:
                    pass
            time.sleep(1)
        except Exception as e:
            print("[Gemini] Cle " + str(key_idx+1) + " " + model + ": " + str(e))
            time.sleep(1)
    return False

def find_all_models():
    print("\n[Gemini] Initialisation de " + str(len(API_KEYS)) + " cle(s)...")
    success = 0
    for i in range(len(API_KEYS)):
        if API_KEYS[i]:
            if find_model_for_key(i):
                success += 1
    print("[Gemini] " + str(success) + "/" + str(len(API_KEYS)) +
          " cle(s) operationnelles")
    return success > 0

def gemini(prompt, max_tokens=65536, retries=3):
    if not ACTIVE_MODELS:
        if not find_all_models():
            return None

    if len(prompt) > 60000:
        prompt = prompt[:60000] + "\n...[TRONQUE]"

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.05,
        }
    }).encode("utf-8")

    total_attempts = retries * max(len(API_KEYS), 1)

    for attempt in range(1, total_attempts + 1):
        key_idx = get_best_key()

        if key_idx not in ACTIVE_MODELS:
            if not find_model_for_key(key_idx):
                continue

        model_info = ACTIVE_MODELS[key_idx]
        url = (model_info["url"].split("?")[0] +
               "?key=" + API_KEYS[key_idx])

        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read().decode())
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                finish = data["candidates"][0].get("finishReason", "STOP")
                print("[Gemini] Cle " + str(key_idx+1) +
                      " -> " + str(len(text)) + " chars (finish=" + finish + ")")
                return text

        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print("[Gemini] Cle " + str(key_idx+1) +
                  " HTTP " + str(e.code) +
                  " tentative " + str(attempt) + "/" + str(total_attempts))

            if e.code == 429:
                wait = min(60 * (1 + KEY_STATE["errors"].get(key_idx, 0)), 300)
                set_key_cooldown(key_idx, wait)
                if len(API_KEYS) > 1:
                    continue
                time.sleep(min(wait, 60))
            elif e.code in (404, 400):
                if key_idx in ACTIVE_MODELS:
                    del ACTIVE_MODELS[key_idx]
                find_model_for_key(key_idx)
            elif e.code == 403:
                try:
                    msg = json.loads(body).get("error", {}).get("message", "")
                    if "leaked" in msg.lower():
                        d("ALERTE SECURITE",
                          "Cle " + str(key_idx+1) + " compromise!", 0xFF0000)
                        sys.exit(1)
                except Exception:
                    pass
                set_key_cooldown(key_idx, 600)
            else:
                time.sleep(20)

        except Exception as e:
            print("[Gemini] Cle " + str(key_idx+1) +
                  " Exception: " + str(e))
            time.sleep(15)

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
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
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
    ctx = "=== CODE SOURCE MAXOS ===\n\n"
    ctx += "FICHIERS:\n"
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
            ctx += "[" + f + " tronque]\n"
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
    return {"files": total_files, "lines": total_lines, "languages": languages}

# ══════════════════════════════════════════════════════
# GIT ET BUILD
# ══════════════════════════════════════════════════════
def git(args):
    r = subprocess.run(
        ["git"] + args, cwd=REPO_PATH,
        capture_output=True, text=True
    )
    return r.returncode == 0, r.stdout, r.stderr

def generate_commit_message(task_name, files_written, description, model_used):
    now = datetime.utcnow()

    # Categorie
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

    files_short = ", ".join(
        [os.path.basename(f) for f in files_written[:4]]
    )
    if len(files_written) > 4:
        files_short += " +" + str(len(files_written) - 4) + " files"

    short = prefix + ": " + task_name + " [" + files_short + "]"

    body = (
        "\n"
        "Component : " + ", ".join(sorted(dirs_touched)) + "\n"
        "Files     : " + ", ".join(files_written) + "\n"
        "Model     : " + model_used + "\n"
        "Timestamp : " + now.strftime("%Y-%m-%dT%H:%M:%SZ") + "\n"
        "\n"
        "Description:\n"
        "  " + description[:300] + "\n"
        "\n"
        "Build: gcc -m32 -ffreestanding -nostdlib | nasm ELF32 | ld elf_i386\n"
        "Target: x86 32-bit Protected Mode | QEMU i386\n"
    )

    return short, short + body

def git_push(task_name, files_written, description, model_used):
    short_msg, full_msg = generate_commit_message(
        task_name, files_written, description, model_used
    )
    git(["add", "-A"])
    ok, out, e = git(["commit", "-m", full_msg])
    if not ok:
        if "nothing to commit" in (out + e):
            print("[Git] Rien a committer")
            return True, None, None
        print("[Git] Commit KO: " + e[:200])
        return False, None, None

    _, sha, _ = git(["rev-parse", "HEAD"])
    sha = sha.strip()[:7]

    ok2, _, e2 = git(["push"])
    if not ok2:
        print("[Git] Push KO: " + e2[:200])
        return False, None, None

    print("[Git] OK Commit " + sha + ": " + short_msg)
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
    warnings = []
    for line in log.split("\n"):
        ll = line.lower()
        if "error:" in ll:
            errors.append(line.strip())
        elif "warning:" in ll:
            warnings.append(line.strip())

    print("[Build] " + ("OK" if ok else "ECHEC") +
          " (" + str(len(errors)) + " erreurs, " +
          str(len(warnings)) + " warnings)")
    if not ok:
        for e in errors[:8]:
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
                to_delete.append(fname)
                print("[Parse] DELETE demande: " + fname)
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
            print("[Write] Chemin suspect ignore: " + path)
            continue
        full = os.path.join(REPO_PATH, path)
        parent = os.path.dirname(full)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        written.append(path)
        print("[Write] OK " + path + " (" + str(len(content)) + " chars)")
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
    print("[Restore] " + str(len(backups)) + " fichier(s) restaure(s)")

# ══════════════════════════════════════════════════════
# PHASE 1 : ANALYSE
# ══════════════════════════════════════════════════════
def phase_analyse(context, stats):
    print("\n[Phase 1] Analyse en cours...")

    prompt = (
        "Tu es un expert OS bare metal x86.\n\n" +
        BARE_METAL_RULES + "\n\n" +
        OS_MISSION + "\n\n" +
        context + "\n\n" +
        "STATS DU PROJET:\n"
        "- Fichiers: " + str(stats["files"]) + "\n"
        "- Lignes: " + str(stats["lines"]) + "\n\n"
        "Analyse MaxOS et retourne UNIQUEMENT ce JSON valide.\n"
        "PAS de texte avant ou apres, PAS de ```json.\n"
        "Commence directement par { :\n\n"
        "{\n"
        '  "score_actuel": 45,\n'
        '  "niveau_os": "Bootloader basique",\n'
        '  "commentaire_global": "Phrase courte",\n'
        '  "fonctionnalites_presentes": ["Boot x86"],\n'
        '  "fonctionnalites_manquantes_critiques": ["IDT", "Timer"],\n'
        '  "problemes_critiques": [\n'
        '    {"fichier": "kernel/kernel.c", "description": "probleme", "impact": "CRITIQUE"}\n'
        '  ],\n'
        '  "fichiers_obsoletes": [],\n'
        '  "plan_ameliorations": [\n'
        '    {\n'
        '      "nom": "Nom technique precis",\n'
        '      "priorite": "CRITIQUE",\n'
        '      "categorie": "kernel",\n'
        '      "fichiers_a_modifier": ["kernel/kernel.c"],\n'
        '      "fichiers_a_creer": [],\n'
        '      "fichiers_a_supprimer": [],\n'
        '      "description": "Description technique precise",\n'
        '      "impact_attendu": "Ce que l utilisateur verra",\n'
        '      "complexite": "HAUTE"\n'
        '    }\n'
        '  ],\n'
        '  "prochaine_milestone": "Kernel stable IDT+Timer+Memory"\n'
        "}"
    )

    response = gemini(prompt, max_tokens=4000)
    if not response:
        return None

    print("[Phase 1] " + str(len(response)) + " chars recus")

    clean = response.strip()
    if clean.startswith("```"):
        lines = clean.split("\n")[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        clean = "\n".join(lines).strip()

    # Nettoyer les backslashes problematiques
    clean = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', clean)

    for attempt in range(3):
        i = clean.find("{")
        j = clean.rfind("}") + 1
        if i >= 0 and j > i:
            try:
                return json.loads(clean[i:j])
            except json.JSONDecodeError as e:
                print("[Phase 1] JSON erreur tentative " +
                      str(attempt+1) + ": " + str(e))

    # Plan par defaut ambitieux
    print("[Phase 1] Utilisation plan par defaut ambitieux")
    return {
        "score_actuel": 30,
        "niveau_os": "Prototype bare metal",
        "commentaire_global": "OS fonctionnel basique, nombreuses ameliorations possibles",
        "fonctionnalites_presentes": [
            "Boot x86", "Mode texte VGA", "Keyboard PS/2", "Apps basiques"
        ],
        "fonctionnalites_manquantes_critiques": [
            "IDT complete", "Timer PIT", "Gestionnaire memoire",
            "Mode graphique VESA", "Systeme de fichiers"
        ],
        "problemes_critiques": [],
        "fichiers_obsoletes": [],
        "plan_ameliorations": [
            {
                "nom": "IDT complete + handlers exceptions x86",
                "priorite": "CRITIQUE",
                "categorie": "kernel",
                "fichiers_a_modifier": [
                    "kernel/kernel.c", "kernel/kernel_entry.asm"
                ],
                "fichiers_a_creer": ["kernel/idt.h", "kernel/idt.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "Implementer IDT 256 entrees, handlers exceptions 0-31 "
                    "(division zero, page fault, GPF), IRQ hardware 0-15. "
                    "Stubs NASM pour chaque vecteur. PIC 8259 initialise."
                ),
                "impact_attendu": "OS stable, pas de triple fault",
                "complexite": "HAUTE"
            },
            {
                "nom": "Timer PIT 8253 + compteur ticks + sleep()",
                "priorite": "CRITIQUE",
                "categorie": "kernel",
                "fichiers_a_modifier": ["kernel/kernel.c"],
                "fichiers_a_creer": ["kernel/timer.h", "kernel/timer.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "Configurer PIT 8253 a 100Hz. Compteur global de ticks. "
                    "Fonctions timer_init(), timer_ticks(), sleep_ms(). "
                    "Afficher uptime dans sysinfo."
                ),
                "impact_attendu": "Animations, horloge systeme, base scheduler",
                "complexite": "MOYENNE"
            },
            {
                "nom": "Allocateur memoire physique bitmap 4KB",
                "priorite": "HAUTE",
                "categorie": "kernel",
                "fichiers_a_modifier": ["kernel/kernel.c"],
                "fichiers_a_creer": ["kernel/memory.h", "kernel/memory.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "Bitmap allocator pour pages 4KB. Zone 1MB-16MB. "
                    "Fonctions mem_init(), mem_alloc(), mem_free(). "
                    "Afficher stats memoire dans sysinfo."
                ),
                "impact_attendu": "Allocation dynamique, base pour apps complexes",
                "complexite": "HAUTE"
            },
            {
                "nom": "Terminal 20 commandes + historique circulaire",
                "priorite": "HAUTE",
                "categorie": "app",
                "fichiers_a_modifier": [
                    "apps/terminal.h", "apps/terminal.c"
                ],
                "fichiers_a_creer": [],
                "fichiers_a_supprimer": [],
                "description": (
                    "Commandes: help, ver, mem, uptime, cls, echo, date, "
                    "reboot, halt, color, ps, edit, calc, beep, ls, cat, "
                    "mkdir, rm, cp, mv. "
                    "Historique circulaire 20 entrees (fleches haut/bas). "
                    "Autocompletion TAB basique."
                ),
                "impact_attendu": "Terminal puissant type cmd.exe",
                "complexite": "MOYENNE"
            },
            {
                "nom": "Interface graphique VGA mode 13h 320x200",
                "priorite": "NORMALE",
                "categorie": "driver",
                "fichiers_a_modifier": [
                    "drivers/screen.h", "drivers/screen.c",
                    "kernel/kernel.c"
                ],
                "fichiers_a_creer": ["drivers/vga.h", "drivers/vga.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "Mode graphique VGA mode 13h (320x200, 256 couleurs). "
                    "Fonctions vga_init(), vga_pixel(x,y,color), "
                    "vga_rect(), vga_clear(), vga_text(). "
                    "Desktop avec degrade de couleurs. "
                    "Conserver fallback mode texte si echec."
                ),
                "impact_attendu": "Interface graphique coloree",
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
    print("[Impl] Cat: " + categorie + " | Complexite: " + complexite)
    print("       Modifier:  " + str(fichiers_m))
    print("       Creer:     " + str(fichiers_c))
    print("       Supprimer: " + str(fichiers_s))

    # Contexte cible
    lies = set(tous)
    for f in tous:
        base = f.replace(".c", "").replace(".h", "")
        for ext in [".c", ".h"]:
            candidate = base + ext
            if candidate in all_sources:
                lies.add(candidate)

    for key in ["kernel/kernel.c", "drivers/screen.h",
                "drivers/screen.c", "drivers/keyboard.h",
                "ui/ui.h", "ui/ui.c", "Makefile",
                "linker.ld", "kernel/kernel_entry.asm"]:
        lies.add(key)

    ctx = "=== FICHIERS CONCERNES ===\n\n"
    for f in sorted(lies):
        c = all_sources.get(f, "")
        ctx += "--- " + f + " ---\n"
        ctx += (c if c else "[MANQUANT - A CREER]") + "\n\n"

    prompt = (
        "Tu es un expert OS bare metal x86. Tu developpes MaxOS.\n\n" +
        BARE_METAL_RULES + "\n\n" +
        OS_MISSION + "\n\n" +
        ctx + "\n"
        "══════════════════════════\n"
        "TACHE : " + nom + "\n"
        "CATEGORIE : " + categorie + "\n"
        "COMPLEXITE : " + complexite + "\n"
        "DESCRIPTION : " + desc + "\n"
        "IMPACT : " + impact + "\n"
        "FICHIERS A MODIFIER : " + str(fichiers_m) + "\n"
        "FICHIERS A CREER    : " + str(fichiers_c) + "\n"
        "FICHIERS A SUPPRIMER: " + str(fichiers_s) + "\n"
        "══════════════════════════\n\n"
        "INSTRUCTIONS :\n"
        "1. Code COMPLET dans chaque fichier\n"
        "2. JAMAIS de '// reste inchange' ou '...'\n"
        "3. Nouveaux .c -> mettre a jour Makefile\n"
        "4. Pour supprimer: === DELETE: chemin ===\n"
        "5. Chaque amelioration visible dans QEMU\n"
        "6. Commenter le code avec /* */\n\n"
        "FORMAT DE REPONSE:\n"
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
        d("Echec: " + nom, "Gemini n'a pas repondu", 0xFF0000)
        return False, [], []

    print("[Impl] " + str(len(response)) +
          " chars en " + str(round(elapsed, 1)) + "s")

    files, to_delete = parse_files(response)

    if not files and not to_delete:
        print("[Debug] Debut reponse:\n" + response[:600])
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
        fixed = auto_fix(log, errors, files, backs)
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
def auto_fix(build_log, errors, generated_files, backups, max_attempts=2):
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

        error_txt = "\n".join(errors[:15])

        prompt = (
            "Corrige ces erreurs de compilation bare metal x86.\n\n" +
            BARE_METAL_RULES + "\n\n"
            "ERREURS :\n```\n" + error_txt + "\n```\n\n"
            "LOG (fin):\n```\n" + build_log[-2000:] + "\n```\n\n"
            "FICHIERS ACTUELS :\n" + ctx + "\n"
            "REGLES : Code complet, pas de librairies standard.\n\n"
            "=== FILE: fichier_a_corriger.c ===\n"
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
            current_model = ACTIVE_MODELS.get(
                KEY_STATE["current_index"], {}
            ).get("model", "gemini")
            git_push(
                "auto-fix: correction erreurs compilation",
                list(files.keys()),
                "Correction auto: " + str(len(errors)) + " erreurs -> 0",
                current_model
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
# GESTION AUTOMATIQUE DES PULL REQUESTS
# ══════════════════════════════════════════════════════
def handle_pull_requests():
    """Review et merge automatique des PRs."""
    prs = github_get_open_prs()
    if not prs:
        print("[PR] Aucune PR ouverte")
        return

    print("[PR] " + str(len(prs)) + " PR(s) ouverte(s)")

    for pr in prs:
        pr_number = pr.get("number")
        pr_title = pr.get("title", "")
        pr_author = pr.get("user", {}).get("login", "unknown")
        pr_body = pr.get("body", "") or ""

        print("[PR] Analyse PR #" + str(pr_number) + ": " + pr_title)

        # Recuperer les fichiers modifies
        files_data = github_api("GET", "pulls/" + str(pr_number) + "/files")
        if not files_data:
            continue

        file_list = "\n".join([
            "- " + f.get("filename", "?") +
            " (+" + str(f.get("additions", 0)) +
            " -" + str(f.get("deletions", 0)) + ")"
            for f in files_data[:20]
        ])

        patches = ""
        for f in files_data[:5]:
            fname = f.get("filename", "")
            patch = f.get("patch", "")[:800]
            if patch:
                patches += "--- " + fname + " ---\n" + patch + "\n\n"

        prompt = (
            "Tu es le mainteneur de MaxOS, un OS bare metal x86.\n\n" +
            BARE_METAL_RULES + "\n\n"
            "Pull Request #" + str(pr_number) + " : " + pr_title + "\n"
            "Auteur: " + pr_author + "\n"
            "Description: " + pr_body[:500] + "\n\n"
            "Fichiers modifies:\n" + file_list + "\n\n"
            "Changements:\n" + patches + "\n\n"
            "DECISION (reponds en JSON simple):\n"
            "{\n"
            '  "action": "MERGE" ou "REJECT",\n'
            '  "raison": "explication courte",\n'
            '  "commentaire": "commentaire pour le developpeur"\n'
            "}\n\n"
            "MERGER si: le code compile, respecte bare metal, ameliore l OS.\n"
            "REJETER si: utilise librairies standard, casse le build, "
            "code dangereux.\n"
            "Commence par { :"
        )

        response = gemini(prompt, max_tokens=1000)
        if not response:
            continue

        # Parser la decision
        try:
            clean = response.strip()
            if clean.startswith("```"):
                clean = "\n".join(clean.split("\n")[1:])
                if clean.endswith("```"):
                    clean = clean[:-3]
            i = clean.find("{")
            j = clean.rfind("}") + 1
            decision = json.loads(clean[i:j])
            action = decision.get("action", "REJECT")
            raison = decision.get("raison", "")
            commentaire = decision.get("commentaire", "")
        except Exception:
            action = "REJECT"
            raison = "Impossible d'analyser"
            commentaire = "Review automatique echouee"

        comment_body = (
            "## Review automatique MaxOS AI v8.0\n\n"
            "**Decision:** " + action + "\n"
            "**Raison:** " + raison + "\n\n"
            + commentaire + "\n\n"
            "---\n"
            "*Review par MaxOS AI Developer v8.0*"
        )

        github_comment_pr(pr_number, comment_body)

        if action == "MERGE":
            success = github_merge_pr(pr_number, pr_title)
            if success:
                d(
                    "PR #" + str(pr_number) + " mergee automatiquement",
                    "**Titre:** " + pr_title + "\n**Raison:** " + raison,
                    0x00FF88
                )
                print("[PR] Merge OK: #" + str(pr_number))
            else:
                print("[PR] Merge echec: #" + str(pr_number))
        else:
            github_close_pr(pr_number, comment_body)
            d(
                "PR #" + str(pr_number) + " rejetee",
                "**Titre:** " + pr_title + "\n**Raison:** " + raison,
                0xFF4444
            )
            print("[PR] Rejetee: #" + str(pr_number))

# ══════════════════════════════════════════════════════
# RELEASE GITHUB
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
        new_tag = "v" + str(parts[0]) + "." + str(parts[1]) + "." + str(parts[2])
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
            changes_md += ("  - Fichiers: `" +
                          "`, `".join(files[:5]) + "`\n")
        if model:
            changes_md += "  - Modele IA: `" + model + "`\n"

    failed_md = ""
    for t in tasks_failed:
        failed_md += "- ~~" + t + "~~ (reporte)\n"

    features_md = "\n".join(["  - " + f for f in features]) or "  - Boot x86 basique"

    lang_stats = "\n".join([
        "  | " + (ext or "Makefile") + " | " + str(lines) + " lignes |"
        for ext, lines in sorted(
            stats.get("languages", {}).items(),
            key=lambda x: -x[1]
        )[:6]
    ])

    keys_used = sum(
        1 for i in range(len(API_KEYS))
        if KEY_STATE["usage_count"].get(i, 0) > 0
    )

    models_used = ", ".join([
        ACTIVE_MODELS.get(i, {}).get("model", "?")
        for i in range(len(API_KEYS))
        if i in ACTIVE_MODELS
    ])

    release_body = (
        "# MaxOS " + new_tag + "\n\n"
        "> **Release generee automatiquement par MaxOS AI Developer v8.0**\n"
        "> Objectif : OS a l'echelle de Windows 11, developpe par IA\n\n"
        "---\n\n"
        "## Etat du projet\n\n"
        "| Metrique | Valeur |\n"
        "|----------|--------|\n"
        "| Score global | " + str(score) + "/100 |\n"
        "| Niveau actuel | " + niveau + " |\n"
        "| Fichiers | " + str(stats.get("files", 0)) + " |\n"
        "| Lignes de code | " + str(stats.get("lines", 0)) + " |\n"
        "| Prochaine milestone | " + milestone + " |\n\n"
        "---\n\n"
        "## Changements de cette release\n\n" +
        (changes_md or "- Maintenance interne\n") + "\n"
        + ("## Reporte au prochain cycle\n\n" + failed_md + "\n" if failed_md else "") +
        "---\n\n"
        "## Fonctionnalites actuelles\n\n" +
        features_md + "\n\n"
        "---\n\n"
        "## Statistiques du code\n\n"
        "| Langage | Lignes |\n"
        "|---------|--------|\n" +
        lang_stats + "\n\n"
        "---\n\n"
        "## Tester MaxOS\n\n"
        "### Option 1 - Telecharger et lancer\n\n"
        "```bash\n"
        "# Telecharger os.img depuis les Artifacts GitHub Actions\n"
        "# (onglet Actions -> dernier run -> Artifacts -> maxos-build-XXX)\n\n"
        "# Ubuntu/Debian\n"
        "sudo apt install qemu-system-x86\n"
        "qemu-system-i386 -drive format=raw,file=os.img,if=floppy "
        "-boot a -vga std -k fr -m 32 -no-reboot\n\n"
        "# Windows : installer QEMU depuis https://www.qemu.org/windows/\n"
        "# Puis dans PowerShell (adapter le chemin) :\n"
        'qemu-system-i386.exe -drive format=raw,file=os.img,'
        'if=floppy -boot a -vga std -k fr -m 32\n'
        "```\n\n"
        "### Option 2 - Compiler depuis les sources\n\n"
        "```bash\n"
        "sudo apt install nasm gcc make gcc-multilib qemu-system-x86\n"
        "git clone https://github.com/" + REPO_OWNER + "/" + REPO_NAME + ".git\n"
        "cd MaxOS\n"
        "make\n"
        "make run\n"
        "```\n\n"
        "---\n\n"
        "## Controles dans QEMU\n\n"
        "| Touche | Action |\n"
        "|--------|--------|\n"
        "| **TAB** | Changer d'application |\n"
        "| **F1** | Bloc-Notes |\n"
        "| **F2** | Terminal |\n"
        "| **F3** | Informations systeme |\n"
        "| **F4** | A propos |\n"
        "| **Echap** | Retour bureau |\n\n"
        "---\n\n"
        "## Informations techniques\n\n"
        "| Composant | Detail |\n"
        "|-----------|--------|\n"
        "| Architecture | x86 32-bit Protected Mode |\n"
        "| Compilateur | GCC `-m32 -ffreestanding -nostdlib -nostdinc` |\n"
        "| Assembleur | NASM ELF32 |\n"
        "| Editeur de liens | GNU LD avec script custom |\n"
        "| Emulateur cible | QEMU i386 |\n"
        "| IA developpeur | " + models_used + " |\n"
        "| Cles IA utilisees | " + str(keys_used) + "/" + str(len(API_KEYS)) + " |\n\n"
        "---\n\n"
        "## Roadmap\n\n"
        "| Phase | Statut | Description |\n"
        "|-------|--------|-------------|\n"
        "| Phase 1 | En cours | Fondations kernel (IDT, Timer, Memoire) |\n"
        "| Phase 2 | Planifie | Mode graphique VESA |\n"
        "| Phase 3 | Planifie | Systeme de fichiers FAT12 |\n"
        "| Phase 4 | Planifie | Interface fenetree + souris |\n"
        "| Phase 5 | Planifie | Applications avancees |\n"
        "| Phase 6 | Futur | Stack reseau TCP/IP |\n\n"
        "---\n\n"
        "*Prochain cycle automatique | MaxOS AI Developer v8.0 | " +
        now.strftime("%Y-%m-%d %H:%M") + " UTC*\n"
    )

    url = github_create_release(
        tag=new_tag,
        name="MaxOS " + new_tag + " - " + niveau + " | " + now.strftime("%Y-%m-%d"),
        body=release_body,
        prerelease=(score < 50)
    )

    if url:
        d(
            "Release " + new_tag + " publiee",
            "Niveau : " + niveau + "\nScore : " + str(score) + "/100\n" + url,
            0x00FF88,
            [
                {"name": "Version",   "value": new_tag,              "inline": True},
                {"name": "Score",     "value": str(score) + "/100",  "inline": True},
                {"name": "Succes",    "value": str(len(tasks_done)), "inline": True},
                {"name": "Milestone", "value": milestone[:50],       "inline": False},
                {"name": "Lien",
                 "value": "[Voir la release](" + url + ")",
                 "inline": False},
            ]
        )

    return url

# ══════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("  MaxOS AI Developer v8.0")
    print("  Objectif: OS echelle Windows 11")
    print("  Mode: Autonome 24/7 | Multi-cles | Auto PR/Release")
    print("=" * 60 + "\n")

    if not find_all_models():
        print("FATAL: Aucune cle Gemini operationnelle")
        sys.exit(1)

    current_model = ACTIVE_MODELS.get(0, {}).get("model", "?")

    d(
        "MaxOS AI Developer v8.0 demarre",
        ("Objectif: OS a l'echelle de Windows 11\n"
         "Cles actives: " + str(len(ACTIVE_MODELS)) +
         "/" + str(len(API_KEYS))),
        0x5865F2,
        [
            {"name": "Modeles",
             "value": "\n".join([
                 "Cle " + str(i+1) + ": " + ACTIVE_MODELS[i]["model"]
                 for i in sorted(ACTIVE_MODELS.keys())
             ]),
             "inline": False},
            {"name": "Repo",
             "value": REPO_OWNER + "/" + REPO_NAME,
             "inline": True},
            {"name": "Heure",
             "value": datetime.now().strftime("%H:%M:%S"),
             "inline": True},
        ]
    )

    # Gestion des PRs ouvertes
    print("\n[PRs] Verification des pull requests...")
    handle_pull_requests()

    # Sources
    sources = read_all()
    context = build_context(sources)
    stats = get_project_stats(sources)
    print("[Sources] " + str(stats["files"]) + " fichiers, " +
          str(stats["lines"]) + " lignes, " +
          str(len(context)) + " chars")

    # Phase 1
    print("\n" + "="*60)
    print(" PHASE 1 : Analyse")
    print("="*60)

    analyse = phase_analyse(context, stats)
    if not analyse:
        d("Analyse echouee", "Impossible d'analyser le code.", 0xFF0000)
        sys.exit(1)

    score = analyse.get("score_actuel", 0)
    niveau = analyse.get("niveau_os", "?")
    plan = analyse.get("plan_ameliorations", [])
    milestone = analyse.get("prochaine_milestone", "?")
    features = analyse.get("fonctionnalites_presentes", [])
    manquantes = analyse.get("fonctionnalites_manquantes_critiques", [])

    print("[Rapport] Score: " + str(score) + "/100")
    print("[Rapport] Niveau: " + niveau)
    print("[Rapport] " + str(len(plan)) + " ameliorations planifiees")
    print("[Rapport] Milestone: " + milestone)

    features_txt = "\n".join(["+ " + f for f in features[:5]]) or "Aucune"
    manquantes_txt = "\n".join(["- " + f for f in manquantes[:5]]) or "Aucune"
    plan_txt = "\n".join([
        "[" + str(i+1) + "] [" + t.get("priorite", "?") + "] " + t.get("nom", "?")
        for i, t in enumerate(plan[:6])
    ])

    d(
        "Rapport - Score " + str(score) + "/100",
        "```\n" + progress_bar(score) + "\n```\nNiveau: " + niveau,
        0x00AAFF if score >= 60 else 0xFFA500 if score >= 30 else 0xFF4444,
        [
            {"name": "Fonctionnalites presentes",
             "value": features_txt[:512], "inline": True},
            {"name": "A implementer",
             "value": manquantes_txt[:512], "inline": True},
            {"name": "Plan du cycle",
             "value": "```\n" + plan_txt + "\n```", "inline": False},
            {"name": "Prochaine milestone",
             "value": milestone[:100], "inline": False},
            {"name": "Etat des cles",
             "value": key_status_str(), "inline": False},
        ]
    )

    # Phase 2
    print("\n" + "="*60)
    print(" PHASE 2 : Implementation")
    print("="*60)

    order = {"CRITIQUE": 0, "HAUTE": 1, "NORMALE": 2, "BASSE": 3}
    plan_sorted = sorted(
        plan, key=lambda x: order.get(x.get("priorite", "NORMALE"), 2)
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
        print(" [" + str(i) + "/" + str(total) + "] [" + priorite + "] " + nom)
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
                {"name": "Priorite",   "value": priorite,    "inline": True},
                {"name": "Categorie",  "value": categorie,   "inline": True},
                {"name": "Modele",     "value": current_model, "inline": True},
            ]
        )

        sources = read_all()
        ok, written, deleted = phase_implement(task, sources)

        _, latest_sha, _ = git(["rev-parse", "HEAD"])
        latest_sha = latest_sha.strip()[:7]

        if ok:
            success += 1
            task_record = {
                "nom": nom,
                "files": written + deleted,
                "sha": latest_sha,
                "model": current_model,
            }
            tasks_done.append(task_record)

            d(
                "Succes: " + nom,
                "Amelioration appliquee et commitee.",
                0x00FF88,
                [
                    {"name": "Fichiers ecrits",
                     "value": "\n".join(["`" + f + "`" for f in written[:5]])
                              or "Aucun",
                     "inline": True},
                    {"name": "Fichiers supprimes",
                     "value": "\n".join(["`" + f + "`" for f in deleted])
                              or "Aucun",
                     "inline": True},
                    {"name": "Commit",
                     "value": "`" + latest_sha + "`",
                     "inline": True},
                ]
            )
            sources = read_all()
        else:
            tasks_failed.append(nom)
            d(
                "Echec: " + nom,
                "Code restaure. Reporte au prochain cycle.",
                0xFF6600
            )

        if i < total:
            pause = 15 if len(API_KEYS) > 1 else 30
            print("[Pause] " + str(pause) + "s...")
            time.sleep(pause)

    # Release
    if success > 0:
        print("\n[Release] Creation release GitHub...")
        sources = read_all()
        stats = get_project_stats(sources)
        create_release(tasks_done, tasks_failed, analyse, stats)

    # Rapport final
    pct = int(success / total * 100) if total > 0 else 0
    color = 0x00FF88 if pct >= 80 else 0xFFA500 if pct >= 50 else 0xFF4444

    d(
        "Cycle termine - " + str(success) + "/" + str(total) + " reussies",
        "```\n" + progress_bar(pct) + "\n```\nProchain cycle automatique.",
        color,
        [
            {"name": "Succes",  "value": str(success),        "inline": True},
            {"name": "Echecs",  "value": str(total-success),  "inline": True},
            {"name": "Taux",    "value": str(pct) + "%",      "inline": True},
            {"name": "Cles",    "value": key_status_str(),    "inline": False},
            {"name": "Taches reussies",
             "value": "\n".join(["- " + t["nom"][:50]
                                for t in tasks_done])[:512] or "Aucune",
             "inline": False},
        ]
    )

    print("\n[FIN] " + str(success) + "/" + str(total) +
          " ameliorations. Prochain cycle automatique.")

if __name__ == "__main__":
    main()
