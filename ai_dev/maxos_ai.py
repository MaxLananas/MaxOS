#!/usr/bin/env python3
"""MaxOS AI Developer v7.0"""

import os, sys, json, time, subprocess
import urllib.request, urllib.error
from datetime import datetime

# ══════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════
GEMINI_API_KEY  = os.environ.get("GEMINI_API_KEY", "")
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")
GITHUB_TOKEN    = os.environ.get("GITHUB_TOKEN", "")
REPO_OWNER      = os.environ.get("REPO_OWNER", "MaxLananas")
REPO_NAME       = os.environ.get("REPO_NAME", "MaxOS")
REPO_PATH       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KEY_MASKED = (GEMINI_API_KEY[:4] + "*" * max(0, len(GEMINI_API_KEY)-8) + GEMINI_API_KEY[-4:]) if len(GEMINI_API_KEY) > 8 else "***"

print(f"[Config] Gemini  : {KEY_MASKED}")
print(f"[Config] Discord : {'OK' if DISCORD_WEBHOOK else 'ABSENT'}")
print(f"[Config] GitHub  : {'OK' if GITHUB_TOKEN else 'ABSENT'}")
print(f"[Config] Repo    : {REPO_OWNER}/{REPO_NAME}")
print(f"[Config] Path    : {REPO_PATH}")

if not GEMINI_API_KEY:
    print("FATAL: GEMINI_API_KEY manquante")
    sys.exit(1)

# Modèles à tester
MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
]

WORKING_MODEL = None
WORKING_URL   = None

# Tous les fichiers du projet
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

# Règles bare metal inviolables
BARE_METAL_RULES = """
REGLES ABSOLUES BARE METAL x86 (VIOLATION = ECHEC DE COMPILATION) :

1. ZERO include de librairie standard :
   - PAS #include <stddef.h>
   - PAS #include <string.h>
   - PAS #include <stdlib.h>
   - PAS #include <stdio.h>
   - PAS #include <stdint.h>
   - PAS #include <stdbool.h>

2. ZERO types de librairie :
   - PAS size_t  -> utilise unsigned int
   - PAS NULL    -> utilise 0
   - PAS bool    -> utilise int
   - PAS true/false -> utilise 1/0
   - PAS uint32_t -> utilise unsigned int
   - PAS int32_t  -> utilise int

3. ZERO fonctions de librairie :
   - PAS malloc/free -> pas d'allocation dynamique
   - PAS memset/memcpy -> boucle for manuelle
   - PAS strlen/strcmp/strcpy -> fonctions manuelles
   - PAS printf/sprintf -> utiliser v_str() de screen.h

4. FONCTIONS EXISTANTES A RESPECTER :
   - nb_init(), np_draw(), np_key(char k) -> notepad
   - tm_init(), tm_draw(), tm_key(char k) -> terminal
   - si_draw() -> sysinfo (PAS si_init, PAS si_key)
   - ab_draw() -> about   (PAS ab_init, PAS ab_key)
   - kb_init(), kb_haskey(), kb_getchar() -> keyboard
   - v_init(), v_put(), v_str(), v_fill() -> screen

5. ASSEMBLY NASM :
   - PAS de directives C dans les fichiers .asm
   - Utiliser [BITS 32] correctement
   - Les macros IDT doivent utiliser dq, pas des instructions C

6. COMPILATION :
   gcc -m32 -ffreestanding -fno-stack-protector -fno-builtin -fno-pic -fno-pie -nostdlib -nostdinc -w -c
   nasm -f elf (pour .o) / nasm -f bin (pour boot.bin)
   ld -m elf_i386 -T linker.ld --oformat binary
"""

# ══════════════════════════════════════════
# GITHUB API
# ══════════════════════════════════════════
def github_api(method, endpoint, data=None):
    """Appelle l'API GitHub."""
    if not GITHUB_TOKEN:
        return None

    url     = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/{endpoint}"
    payload = json.dumps(data).encode() if data else None

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
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
        print(f"[GitHub API] {method} {endpoint} -> HTTP {e.code}: {body[:200]}")
        return None
    except Exception as e:
        print(f"[GitHub API] Erreur: {e}")
        return None

def github_create_release(tag, name, body, prerelease=False):
    """Crée une release GitHub."""
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
        print(f"[GitHub] Release creee: {result['html_url']}")
        return result["html_url"]
    return None

def github_create_issue(title, body, labels=None):
    """Crée une issue GitHub."""
    data = {
        "title": title,
        "body": body,
        "labels": labels or [],
    }
    result = github_api("POST", "issues", data)
    if result and "html_url" in result:
        print(f"[GitHub] Issue: {result['html_url']}")
        return result["html_url"]
    return None

def github_get_latest_commits(n=10):
    """Récupère les derniers commits."""
    result = github_api("GET", f"commits?per_page={n}")
    if not result:
        return []
    commits = []
    for c in result:
        msg = c.get("commit", {}).get("message", "")
        sha = c.get("sha", "")[:7]
        commits.append(f"{sha}: {msg.split(chr(10))[0]}")
    return commits

# ══════════════════════════════════════════
# DISCORD
# ══════════════════════════════════════════
def discord_send(embeds):
    if not DISCORD_WEBHOOK:
        return

    payload = json.dumps({
        "username": "MaxOS AI Bot",
        "embeds": embeds[:10]
    }).encode("utf-8")

    req = urllib.request.Request(
        DISCORD_WEBHOOK, data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "DiscordBot (MaxOS, 7.0)",
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"[Discord] OK ({r.status})")
            return True
    except urllib.error.HTTPError as e:
        print(f"[Discord] HTTP {e.code}: {e.read().decode()[:200]}")
    except Exception as e:
        print(f"[Discord] Err: {e}")
    return False

def make_embed(title, desc, color, fields=None):
    e = {
        "title": str(title)[:256],
        "description": str(desc)[:4096],
        "color": color,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "footer": {
            "text": f"MaxOS AI v7.0  |  {WORKING_MODEL or 'init'}  |  {REPO_OWNER}/{REPO_NAME}",
        },
    }
    if fields:
        e["fields"] = fields[:25]
    return e

def d(title, desc, color=0x5865F2, fields=None):
    discord_send([make_embed(title, desc, color, fields)])

def progress_bar(pct, w=28):
    f = int(w * pct / 100)
    return f"[{'█'*f}{'░'*(w-f)}] {pct}%"

# ══════════════════════════════════════════
# GEMINI
# ══════════════════════════════════════════
def find_model():
    global WORKING_MODEL, WORKING_URL
    print("\n[Gemini] Recherche modele...")
    for model in MODELS:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            + model + ":generateContent?key=" + GEMINI_API_KEY
        )
        payload = json.dumps({
            "contents": [{"parts": [{"text": "Reponds: READY"}]}],
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
                txt  = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"[Gemini] OK: {model} -> {txt.strip()}")
                WORKING_MODEL = model
                WORKING_URL   = url
                return True
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"[Gemini] {model}: HTTP {e.code}")
            if e.code == 403:
                try:
                    msg = json.loads(body).get("error", {}).get("message", "")
                    if "leaked" in msg.lower():
                        print("FATAL: Cle API compromise!")
                        d("ALERTE SECURITE", "Cle Gemini compromise. Creer une nouvelle cle.", 0xFF0000)
                        sys.exit(1)
                except Exception:
                    pass
            time.sleep(2)
        except Exception as e:
            print(f"[Gemini] {model}: {e}")
            time.sleep(2)
    return False

def gemini(prompt, max_tokens=65536, retries=3):
    global WORKING_URL, WORKING_MODEL

    if not WORKING_URL:
        if not find_model():
            return None

    if len(prompt) > 50000:
        prompt = prompt[:50000] + "\n...[TRONQUE]"

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.05,
        }
    }).encode("utf-8")

    for attempt in range(1, retries+1):
        req = urllib.request.Request(
            WORKING_URL, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data   = json.loads(r.read().decode())
                text   = data["candidates"][0]["content"]["parts"][0]["text"]
                finish = data["candidates"][0].get("finishReason", "STOP")
                print(f"[Gemini] {len(text)} chars (finish={finish})")
                return text
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"[Gemini] HTTP {e.code} tentative {attempt}/{retries}")
            if e.code == 429:
                wait = 70 * attempt
                print(f"[Gemini] Rate limit, attente {wait}s")
                time.sleep(wait)
            elif e.code in (404, 400):
                WORKING_URL = None
                if not find_model():
                    return None
            elif e.code == 403:
                try:
                    msg = json.loads(body).get("error",{}).get("message","")
                    if "leaked" in msg.lower():
                        d("ALERTE", "Cle compromise!", 0xFF0000)
                        sys.exit(1)
                except Exception:
                    pass
                return None
            else:
                time.sleep(20)
        except Exception as e:
            print(f"[Gemini] Exception: {e}")
            time.sleep(15)
    return None

# ══════════════════════════════════════════
# SOURCES
# ══════════════════════════════════════════
def read_all():
    sources = {}
    for f in ALL_FILES:
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                sources[f] = fh.read()
        else:
            sources[f] = None
    return sources

def build_context(sources):
    ctx  = "=== CODE SOURCE COMPLET DE MAXOS ===\n\n"
    ctx += "FICHIERS PRESENTS :\n"
    for f in ALL_FILES:
        s = sources.get(f)
        ctx += f"  {'[OK]' if s else '[MANQUANT]'} {f}\n"
    ctx += "\n"
    for f in ALL_FILES:
        c = sources.get(f)
        ctx += f"{'='*60}\nFICHIER: {f}\n{'='*60}\n"
        ctx += (c if c else "[MANQUANT]\n")
        ctx += "\n\n"
    return ctx

# ══════════════════════════════════════════
# GIT & BUILD
# ══════════════════════════════════════════
def git(args):
    r = subprocess.run(
        ["git"] + args, cwd=REPO_PATH,
        capture_output=True, text=True
    )
    return r.returncode == 0, r.stdout, r.stderr

def git_push(msg):
    git(["add", "-A"])
    ok, out, e = git(["commit", "-m", msg])
    if not ok:
        if "nothing to commit" in (out+e):
            print("[Git] Rien a committer")
            return True, None
        print(f"[Git] Commit KO: {e[:200]}")
        return False, None
    # Récupérer le hash
    _, sha, _ = git(["rev-parse", "HEAD"])
    sha = sha.strip()[:7]

    ok2, _, e2 = git(["push"])
    if not ok2:
        print(f"[Git] Push KO: {e2[:200]}")
        return False, None
    print(f"[Git] Pousse: {msg} [{sha}]")
    return True, sha

def make_build():
    subprocess.run(["make", "clean"], cwd=REPO_PATH, capture_output=True)
    r = subprocess.run(
        ["make"], cwd=REPO_PATH,
        capture_output=True, text=True,
        timeout=120
    )
    ok  = r.returncode == 0
    log = r.stdout + r.stderr
    print(f"[Build] {'OK' if ok else 'ECHEC'}")
    if not ok:
        for line in log.split("\n"):
            if "error:" in line.lower():
                print(f"  {line}")
    return ok, log

# ══════════════════════════════════════════
# PARSER
# ══════════════════════════════════════════
def parse_files(response):
    files     = {}
    cur_file  = None
    cur_lines = []
    in_file   = False

    for line in response.split("\n"):
        s = line.strip()

        if "=== FILE:" in s and s.endswith("==="):
            try:
                start = s.index("=== FILE:") + 9
                end   = s.rindex("===")
                fname = s[start:end].strip().strip("`")
                cur_file  = fname
                cur_lines = []
                in_file   = True
            except Exception:
                pass
            continue

        if s == "=== END FILE ===" and in_file:
            if cur_file:
                content = "\n".join(cur_lines).strip()
                for lang in ["```c","```asm","```nasm","```makefile","```ld","```"]:
                    if content.startswith(lang):
                        content = content[len(lang):].lstrip("\n")
                        break
                if content.endswith("```"):
                    content = content[:-3].rstrip("\n")
                files[cur_file] = content
            cur_file  = None
            cur_lines = []
            in_file   = False
            continue

        if in_file:
            cur_lines.append(line)

    return files

def write_files(files):
    written = []
    for path, content in files.items():
        if path.startswith("/") or ".." in path:
            continue
        full = os.path.join(REPO_PATH, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        written.append(path)
        print(f"[Write] {path} ({len(content)} chars)")
    return written

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
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(c)
    print(f"[Restore] {len(backups)} fichier(s)")

# ══════════════════════════════════════════
# PHASE 1 : ANALYSE
# ══════════════════════════════════════════
def phase_analyse(context):
    print("\n[Phase 1] Analyse...")

    prompt = f"""Tu es un expert OS bare metal x86.

{BARE_METAL_RULES}

{context}

Analyse le code de MaxOS et retourne UNIQUEMENT ce JSON valide.
Pas de texte avant, pas de texte apres, pas de ```json.
Commence directement par {{ :

{{
  "score_actuel": 45,
  "commentaire_global": "Phrase courte",
  "problemes_critiques": [
    {{"fichier": "kernel/kernel.c", "description": "probleme precis"}}
  ],
  "fichiers_manquants": [],
  "plan_ameliorations": [
    {{
      "nom": "Nom court",
      "priorite": "CRITIQUE",
      "fichiers_a_modifier": ["ui/ui.c"],
      "fichiers_a_creer": [],
      "description": "Description precise"
    }}
  ]
}}"""

    response = gemini(prompt, max_tokens=3000)
    if not response:
        return None

    print(f"[Phase 1] {len(response)} chars")
    print(f"[Phase 1] Debut: {response[:150]}")

    clean = response.strip()

    # Nettoyer les blocs markdown
    if clean.startswith("```"):
        lines = clean.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        clean = "\n".join(lines).strip()

    # Extraire JSON
    for attempt in range(3):
        i = clean.find("{")
        j = clean.rfind("}") + 1
        if i >= 0 and j > i:
            try:
                return json.loads(clean[i:j])
            except json.JSONDecodeError as e:
                print(f"[Phase 1] JSON erreur tentative {attempt+1}: {e}")
                # Essayer de couper à la dernière virgule valide
                clean = clean[i:j-1]

    # Plan par défaut
    print("[Phase 1] Utilisation plan par defaut")
    return {
        "score_actuel": 50,
        "commentaire_global": "Analyse automatique - plan standard",
        "problemes_critiques": [],
        "fichiers_manquants": [],
        "plan_ameliorations": [
            {
                "nom": "Interface UI amelioree",
                "priorite": "HAUTE",
                "fichiers_a_modifier": ["ui/ui.h", "ui/ui.c"],
                "fichiers_a_creer": [],
                "description": "Ameliorer topbar et taskbar style Windows 11"
            },
            {
                "nom": "Terminal avec historique",
                "priorite": "HAUTE",
                "fichiers_a_modifier": ["apps/terminal.h", "apps/terminal.c"],
                "fichiers_a_creer": [],
                "description": "Ajouter historique commandes et nouvelles commandes"
            },
            {
                "nom": "Bloc-Notes ameliore",
                "priorite": "NORMALE",
                "fichiers_a_modifier": ["apps/notepad.h", "apps/notepad.c"],
                "fichiers_a_creer": [],
                "description": "Ameliorer editeur de texte avec meilleur curseur"
            },
        ]
    }

# ══════════════════════════════════════════
# PHASE 2 : IMPLEMENTATION
# ══════════════════════════════════════════
def phase_implement(task, all_sources):
    nom        = task.get("nom", "Amelioration")
    fichiers_m = task.get("fichiers_a_modifier", [])
    fichiers_c = task.get("fichiers_a_creer", [])
    desc       = task.get("description", "")
    tous       = list(set(fichiers_m + fichiers_c))

    print(f"\n[Impl] {nom}")
    print(f"[Impl] Cibles: {tous}")

    # Contexte ciblé
    lies = set(tous)
    for f in tous:
        base = f.replace(".c","").replace(".h","")
        for ext in [".c", ".h"]:
            if (base+ext) in all_sources:
                lies.add(base+ext)

    for key in ["kernel/kernel.c", "drivers/screen.h",
                "drivers/keyboard.h", "ui/ui.h", "Makefile"]:
        lies.add(key)

    ctx = "=== FICHIERS CONCERNES ===\n\n"
    for f in sorted(lies):
        c = all_sources.get(f, "")
        ctx += f"--- {f} ---\n{c if c else '[MANQUANT]'}\n\n"

    prompt = f"""Tu es un expert OS bare metal x86.

{BARE_METAL_RULES}

CONTEXTE MAXOS :
{ctx}

TACHE : {nom}
DESCRIPTION : {desc}
FICHIERS A MODIFIER : {fichiers_m}
FICHIERS A CREER    : {fichiers_c}

INSTRUCTIONS CRITIQUES :
- Code COMPLET dans chaque fichier
- PAS de "// reste inchange" ou "..."
- Respecter EXACTEMENT les signatures des fonctions existantes
- si_draw() et ab_draw() existent deja - ne pas creer si_key/ab_key/si_init/ab_init
- kernel.c doit garder TOUTES les apps (notepad, terminal, sysinfo, about)
- Si nouveau fichier .c : mettre a jour le Makefile

COMMENCE DIRECTEMENT PAR LE PREMIER FICHIER - PAS DE TEXTE AVANT :

=== FILE: chemin/fichier.h ===
[code complet]
=== END FILE ==="""

    t0       = time.time()
    response = gemini(prompt, max_tokens=65536)
    elapsed  = time.time() - t0

    if not response:
        d(f"Echec: {nom}", "Gemini n'a pas repondu", 0xFF0000)
        return False, []

    print(f"[Impl] {len(response)} chars en {elapsed:.1f}s")

    files = parse_files(response)
    if not files:
        print(f"[Debug] Debut reponse:\n{response[:800]}")
        d(f"Echec: {nom}", f"Aucun fichier parse.\n```\n{response[:600]}\n```", 0xFF0000)
        return False, []

    print(f"[Impl] Parse: {list(files.keys())}")

    backs   = backup_files(list(files.keys()))
    written = write_files(files)

    if not written:
        d(f"Echec: {nom}", "Aucun fichier ecrit", 0xFF0000)
        return False, []

    build_ok, log = make_build()

    if build_ok:
        pushed, sha = git_push(f"feat: {nom} [{WORKING_MODEL}]")
        if pushed:
            return True, written
        restore_files(backs)
        return False, []
    else:
        # Auto-fix
        fixed = auto_fix(log, files, backs)
        if fixed:
            return True, written

        restore_files(backs)
        for p in written:
            if p not in backs:
                fp = os.path.join(REPO_PATH, p)
                if os.path.exists(fp):
                    os.remove(fp)

        return False, []

# ══════════════════════════════════════════
# AUTO-FIX
# ══════════════════════════════════════════
def auto_fix(build_log, generated_files, backups):
    print("[Fix] Auto-correction...")

    current = {}
    for p in generated_files:
        fp = os.path.join(REPO_PATH, p)
        if os.path.exists(fp):
            with open(fp, "r") as f:
                current[p] = f.read()

    ctx = ""
    for p, c in current.items():
        ctx += f"--- {p} ---\n{c}\n\n"

    # Extraire les erreurs importantes
    errors = [l for l in build_log.split("\n")
              if "error:" in l.lower() and l.strip()][:15]
    error_txt = "\n".join(errors)

    prompt = f"""Corrige ces erreurs de compilation bare metal x86.

{BARE_METAL_RULES}

ERREURS :
```
{error_txt}
```

LOG COMPLET (fin) :
```
{build_log[-1500:]}
```

FICHIERS ACTUELS :
{ctx}

Corrige UNIQUEMENT les erreurs. Code complet.
Commence directement par le fichier :

=== FILE: chemin/fichier.c ===
[code corrige complet]
=== END FILE ==="""

    response = gemini(prompt, max_tokens=32768)
    if not response:
        return False

    files = parse_files(response)
    if not files:
        return False

    write_files(files)
    ok, log = make_build()

    if ok:
        git_push("fix: Auto-correction erreurs de compilation")
        d("Auto-correction reussie", "Erreurs corrigees automatiquement.", 0x00AAFF)
        return True

    restore_files(backups)
    return False

# ══════════════════════════════════════════
# RELEASE GITHUB
# ══════════════════════════════════════════
def create_release(tasks_done, score_before, score_after=None):
    """Crée une release GitHub professionnelle."""
    if not GITHUB_TOKEN:
        print("[Release] Pas de GITHUB_TOKEN")
        return

    # Récupérer le dernier tag
    result = github_api("GET", "tags?per_page=1")
    last_tag = "v0.0.0"
    if result and len(result) > 0:
        last_tag = result[0].get("name", "v0.0.0")

    # Incrémenter la version
    try:
        parts   = last_tag.lstrip("v").split(".")
        parts   = [int(x) for x in parts]
        parts[2] += 1
        if parts[2] >= 10:
            parts[2] = 0
            parts[1] += 1
        new_tag = f"v{parts[0]}.{parts[1]}.{parts[2]}"
    except Exception:
        new_tag = "v1.0.1"

    # Construire le changelog
    now = datetime.utcnow().strftime("%Y-%m-%d")

    changes = "\n".join([f"- {t}" for t in tasks_done]) if tasks_done else "- Maintenance automatique"

    release_body = f"""# MaxOS {new_tag}

Release generee automatiquement par MaxOS AI Developer v7.0.

## Date de publication

{now}

## Changements

{changes}

## Informations techniques

- Architecture : x86 32-bit Protected Mode
- Compilateur  : GCC -m32 -ffreestanding
- Assembleur   : NASM
- Emulateur    : QEMU i386

## Lancer l'OS

```bash
qemu-system-i386 -drive format=raw,file=os.img,if=floppy -boot a -vga std -k fr
```

## Controles

- TAB : Changer d'application
- F1  : Bloc-Notes
- F2  : Terminal
- F3  : Systeme
- F4  : A propos

## Modele IA utilise

{WORKING_MODEL or "gemini"}
"""

    url = github_create_release(
        tag=new_tag,
        name=f"MaxOS {new_tag} - Build automatique {now}",
        body=release_body,
        prerelease=False
    )

    if url:
        d(
            f"Release {new_tag} publiee",
            f"Une nouvelle release a ete creee sur GitHub.\n{url}",
            0x00FF00,
            [
                {"name": "Version",    "value": new_tag,       "inline": True},
                {"name": "Changements","value": str(len(tasks_done)), "inline": True},
                {"name": "Lien",       "value": f"[Voir la release]({url})", "inline": False},
            ]
        )
    return url

# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
def main():
    print("=" * 55)
    print("  MaxOS AI Developer v7.0")
    print("  Autonome + Releases + GitHub Integration")
    print("=" * 55 + "\n")

    if not find_model():
        print("FATAL: Aucun modele disponible")
        sys.exit(1)

    d(
        "MaxOS AI Developer v7.0 demarre",
        f"Modele : {WORKING_MODEL}\nRepo : {REPO_OWNER}/{REPO_NAME}",
        0x5865F2,
        [
            {"name": "Modele",  "value": WORKING_MODEL, "inline": True},
            {"name": "Heure",   "value": datetime.now().strftime("%H:%M:%S"), "inline": True},
        ]
    )

    # Lire les sources
    sources = read_all()
    context = build_context(sources)
    print(f"[Sources] {len([s for s in sources.values() if s])} fichiers, {len(context)} chars")

    # Phase 1 : Analyse
    print("\n" + "="*55)
    print(" PHASE 1 : Analyse")
    print("="*55)

    analyse = phase_analyse(context)
    if not analyse:
        d("Analyse echouee", "Impossible d'analyser le code.", 0xFF0000)
        sys.exit(1)

    score   = analyse.get("score_actuel", 0)
    comment = analyse.get("commentaire_global", "")
    plan    = analyse.get("plan_ameliorations", [])
    bugs    = analyse.get("problemes_critiques", [])
    manq    = analyse.get("fichiers_manquants", [])

    print(f"\n[Rapport] Score: {score}/100")
    print(f"[Rapport] {comment}")
    print(f"[Rapport] {len(plan)} ameliorations planifiees")

    bugs_txt = "\n".join([
        f"- `{b.get('fichier','?')}` : {b.get('description','')[:80]}"
        for b in bugs[:5]
    ]) or "Aucun probleme critique detecte."

    plan_txt = "\n".join([
        f"- [{a.get('priorite','?')}] {a.get('nom','?')}"
        for a in plan[:8]
    ]) or "Aucun"

    d(
        f"Rapport d'analyse - Score {score}/100",
        f"```\n{progress_bar(score)}\n```\n{comment}",
        0x00FF00 if score >= 70 else 0xFFA500 if score >= 40 else 0xFF0000,
        [
            {"name": "Problemes detectes",  "value": bugs_txt[:1024],  "inline": False},
            {"name": "Plan d'amelioration", "value": plan_txt[:1024],  "inline": False},
            {"name": "Fichiers manquants",  "value": "\n".join([f"- `{f}`" for f in manq]) or "Aucun", "inline": True},
        ]
    )

    # Phase 2 : Implementation
    print("\n" + "="*55)
    print(" PHASE 2 : Implementation")
    print("="*55)

    order    = {"CRITIQUE": 0, "HAUTE": 1, "NORMALE": 2, "BASSE": 3}
    plan_sorted = sorted(plan, key=lambda x: order.get(x.get("priorite","NORMALE"), 2))

    success      = 0
    total        = len(plan_sorted)
    tasks_done   = []

    for i, task in enumerate(plan_sorted, 1):
        nom      = task.get("nom", f"Tache {i}")
        priorite = task.get("priorite", "NORMALE")

        print(f"\n{'='*55}")
        print(f" [{i}/{total}] [{priorite}] {nom}")
        print(f"{'='*55}")

        d(
            f"[{i}/{total}] {nom}",
            f"Priorite : {priorite}\n{task.get('description','')}",
            0xFFA500,
            [{"name": "Position", "value": f"{i}/{total}", "inline": True}]
        )

        sources = read_all()
        ok, written = phase_implement(task, sources)

        if ok:
            success += 1
            tasks_done.append(f"{nom} ({', '.join(written[:3])})")
            d(
                f"Succes : {nom}",
                f"Amelioration appliquee.",
                0x00FF00,
                [
                    {"name": "Fichiers", "value": "\n".join([f"`{f}`" for f in written[:5]]), "inline": False},
                    {"name": "Modele",   "value": WORKING_MODEL, "inline": True},
                ]
            )
            sources = read_all()
            context = build_context(sources)
        else:
            d(f"Echec : {nom}", "Code restaure automatiquement.", 0xFF6600)

        if i < total:
            print(f"[Pause] 30s...")
            time.sleep(30)

    # Creer une release si des ameliorations ont reussi
    if success > 0:
        print(f"\n[Release] Creation release GitHub...")
        create_release(tasks_done, score)

    # Rapport final
    pct   = int(success / total * 100) if total > 0 else 0
    color = 0x00FF00 if pct >= 80 else 0xFFA500 if pct >= 50 else 0xFF4444

    d(
        f"Cycle termine : {success}/{total} reussies",
        f"```\n{progress_bar(pct)}\n```",
        color,
        [
            {"name": "Succes",  "value": str(success),         "inline": True},
            {"name": "Echecs",  "value": str(total-success),   "inline": True},
            {"name": "Taux",    "value": f"{pct}%",            "inline": True},
            {"name": "Modele",  "value": WORKING_MODEL or "?", "inline": True},
        ]
    )

    print(f"\n[FIN] {success}/{total} ameliorations.")

if __name__ == "__main__":
    main()
