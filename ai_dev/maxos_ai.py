#!/usr/bin/env python3
"""MaxOS AI Developer v3.0"""

import os, sys, json, time, subprocess
import urllib.request, urllib.error
from datetime import datetime

# ══════════════════════════════
# CONFIG
# ══════════════════════════════
GEMINI_API_KEY  = "TA_CLE_GEMINI_ICI"
DISCORD_WEBHOOK = "TON_WEBHOOK_ICI"
REPO_PATH       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Modèles gratuits 2025 (par ordre de préférence)
MODELS = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash-8b",
]

SOURCE_FILES = [
    "kernel/kernel.c",
    "drivers/screen.c", "drivers/screen.h",
    "drivers/keyboard.c", "drivers/keyboard.h",
    "ui/ui.c", "ui/ui.h",
    "apps/notepad.c", "apps/terminal.c",
    "apps/sysinfo.c", "apps/about.c",
    "boot/boot.asm", "Makefile", "linker.ld",
]

# ══════════════════════════════
# TROUVER LE BON MODÈLE
# ══════════════════════════════
def find_working_model():
    """Teste les modèles jusqu'à en trouver un qui fonctionne."""
    print("[Gemini] Recherche du modèle disponible...")
    for model in MODELS:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            + model
            + ":generateContent?key="
            + GEMINI_API_KEY
        )
        payload = json.dumps({
            "contents": [{"parts": [{"text": "Dis juste: OK"}]}],
            "generationConfig": {"maxOutputTokens": 10}
        }).encode()
        req = urllib.request.Request(
            url, data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                json.loads(r.read())
                print(f"[Gemini] Modèle OK : {model}")
                return model, url
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"[Gemini] {model} → {e.code}: {body[:100]}")
        except Exception as e:
            print(f"[Gemini] {model} → {e}")
        time.sleep(2)
    return None, None

# ══════════════════════════════
# DISCORD
# ══════════════════════════════
def discord_send(title, message, color=0x0099FF, fields=None):
    if not DISCORD_WEBHOOK or "TON_WEBHOOK" in DISCORD_WEBHOOK:
        print(f"[Discord] Skip: {title}")
        return

    embed = {
        "title": str(title)[:256],
        "description": str(message)[:2000],
        "color": color,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "footer": {"text": "MaxOS AI v3.0"},
        "fields": (fields or [])[:25]
    }
    payload = json.dumps({
        "username": "MaxOS AI Bot",
        "embeds": [embed]
    }).encode("utf-8")

    req = urllib.request.Request(
        DISCORD_WEBHOOK,
        data=payload,
        headers={
            "Content-Type": "application/json",
            # Fix Cloudflare 1010
            "User-Agent": "DiscordBot (MaxOS, 1.0)",
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"[Discord] ✅ {title} (HTTP {r.status})")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[Discord] ❌ {e.code}: {body[:200]}")
    except Exception as e:
        print(f"[Discord] ❌ {e}")

def d_ok(t, m, f=None):   discord_send(f"✅ {t}", m, 0x00FF00, f)
def d_err(t, m):           discord_send(f"❌ {t}", m, 0xFF0000)
def d_info(t, m, f=None):  discord_send(f"ℹ️ {t}", m, 0x0099FF, f)
def d_prog(t, m):          discord_send(f"⚙️ {t}", m, 0xFFAA00)

# ══════════════════════════════
# GEMINI
# ══════════════════════════════
GEMINI_URL   = ""
GEMINI_MODEL = ""

def gemini_ask(prompt, retries=3):
    global GEMINI_URL, GEMINI_MODEL
    if not GEMINI_URL:
        GEMINI_MODEL, GEMINI_URL = find_working_model()
        if not GEMINI_URL:
            print("[Gemini] Aucun modèle disponible !")
            return None

    # Limiter la taille du prompt
    if len(prompt) > 25000:
        prompt = prompt[:25000] + "\n[...tronqué...]"

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 8192,
            "temperature": 0.2,
        }
    }).encode("utf-8")

    for attempt in range(retries):
        req = urllib.request.Request(
            GEMINI_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0",
            },
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read().decode())
                return data["candidates"][0]["content"]["parts"][0]["text"]

        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"[Gemini] HTTP {e.code} tentative {attempt+1}/{retries}")
            print(f"[Gemini] {body[:300]}")

            if e.code == 429:
                wait = 70 * (attempt + 1)
                print(f"[Gemini] Rate limit → attente {wait}s")
                time.sleep(wait)
            elif e.code == 404:
                # Modèle introuvable → en chercher un autre
                print("[Gemini] Modèle introuvable, recherche alternative...")
                GEMINI_URL = ""
                GEMINI_MODEL, GEMINI_URL = find_working_model()
                if not GEMINI_URL:
                    return None
                # Reconstruire la requête
                req = urllib.request.Request(
                    GEMINI_URL,
                    data=payload,
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0",
                    },
                    method="POST"
                )
            else:
                time.sleep(15)

        except Exception as e:
            print(f"[Gemini] Exception: {e}")
            time.sleep(10)

    return None

# ══════════════════════════════
# SOURCES
# ══════════════════════════════
def read_sources():
    s = {}
    for f in SOURCE_FILES:
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                s[f] = fh.read()
    return s

def build_context(sources):
    ctx = ""
    for fname, content in sources.items():
        # Max 2000 chars par fichier pour rester dans les limites
        ctx += f"\n--- {fname} ---\n{content[:2000]}\n"
    return ctx

# ══════════════════════════════
# GIT
# ══════════════════════════════
def git(args):
    r = subprocess.run(
        ["git"] + args, cwd=REPO_PATH,
        capture_output=True, text=True
    )
    return r.returncode == 0, r.stdout, r.stderr

def commit_push(msg):
    git(["add", "-A"])
    ok, _, e = git(["commit", "-m", msg])
    if not ok:
        if "nothing to commit" in e:
            print("[Git] Rien à committer")
            return True
        print(f"[Git] Commit KO: {e}")
        return False
    ok, _, e = git(["push"])
    if not ok:
        print(f"[Git] Push KO: {e}")
        return False
    print(f"[Git] ✅ Push: {msg}")
    return True

def make_build():
    subprocess.run(["make", "clean"], cwd=REPO_PATH, capture_output=True)
    r = subprocess.run(["make"], cwd=REPO_PATH, capture_output=True, text=True)
    return r.returncode == 0, r.stdout + r.stderr

# ══════════════════════════════
# PARSER
# ══════════════════════════════
def parse_files(resp):
    files = {}
    lines = resp.split("\n")
    cur_file, cur_lines, in_file = None, [], False

    for line in lines:
        s = line.strip()
        if s.startswith("=== FILE:") and s.endswith("==="):
            cur_file  = s[9:-3].strip()
            cur_lines = []
            in_file   = True
        elif s == "=== END FILE ===" and in_file:
            if cur_file:
                content = "\n".join(cur_lines).strip()
                # Nettoyer les blocs markdown
                if content.startswith("```"):
                    content = "\n".join(content.split("\n")[1:])
                if content.endswith("```"):
                    content = "\n".join(content.split("\n")[:-1])
                files[cur_file] = content
            cur_file, cur_lines, in_file = None, [], False
        elif in_file:
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

def backup_files(files):
    b = {}
    for path in files:
        full = os.path.join(REPO_PATH, path)
        if os.path.exists(full):
            with open(full, "r") as f:
                b[path] = f.read()
    return b

def restore_files(backups):
    for path, content in backups.items():
        full = os.path.join(REPO_PATH, path)
        with open(full, "w") as f:
            f.write(content)

# ══════════════════════════════
# TÂCHES
# ══════════════════════════════
TASKS = [
    {
        "name": "Analyse",
        "type": "analyse",
        "prompt": """Analyse ce code d'OS bare metal x86 et retourne UNIQUEMENT ce JSON :
{
  "score": 42,
  "bugs": ["bug 1"],
  "ameliorations": ["idée 1", "idée 2"],
  "commentaire": "résumé court"
}
Réponds UNIQUEMENT avec le JSON valide."""
    },
    {
        "name": "Amélioration UI Topbar et Taskbar",
        "type": "code",
        "prompt": """Améliore ui/ui.c et ui/ui.h pour MaxOS.

CONTEXTE : OS bare metal x86 32-bit, VGA texte 80x25, 16 couleurs.
OBJECTIF : Interface style Windows 11, propre et moderne.
RÈGLES : C pur, pas malloc/printf/stdlib, compile avec gcc -m32 -ffreestanding -fno-pic -fno-pie -nostdlib -nostdinc

Améliore :
- Topbar avec de beaux séparateurs ASCII
- Onglets actifs/inactifs bien visibles
- Taskbar bas plus élégante
- Icônes ASCII créatives

FORMAT OBLIGATOIRE :
=== FILE: ui/ui.h ===
[code complet]
=== END FILE ===

=== FILE: ui/ui.c ===
[code complet]
=== END FILE ==="""
    },
    {
        "name": "Amélioration Terminal commandes",
        "type": "code",
        "prompt": """Améliore apps/terminal.c et apps/terminal.h.

CONTEXTE : OS bare metal x86 32-bit.
RÈGLES : C pur, pas malloc/printf/stdlib.

Ajoute :
- Commandes : whoami, pwd, ps, date, ver, color, cls
- Historique 10 entrées (flèche haut/bas)
- Prompt coloré
- Messages d'erreur utiles

FORMAT :
=== FILE: apps/terminal.h ===
[code complet]
=== END FILE ===

=== FILE: apps/terminal.c ===
[code complet]
=== END FILE ==="""
    },
    {
        "name": "Amélioration Bloc-Notes",
        "type": "code",
        "prompt": """Améliore apps/notepad.c et apps/notepad.h.

CONTEXTE : OS bare metal x86 32-bit.
RÈGLES : C pur, pas malloc/printf/stdlib.

Améliore :
- Curseur bloc clignotant visible
- Ligne courante surlignée
- Compteur mots/caractères dans statusbar
- Navigation Home/End/PgUp/PgDn
- Scrolling si texte dépasse

FORMAT :
=== FILE: apps/notepad.h ===
[code complet]
=== END FILE ===

=== FILE: apps/notepad.c ===
[code complet]
=== END FILE ==="""
    },
    {
        "name": "Nouvelle App Calculatrice",
        "type": "code",
        "prompt": """Crée une calculatrice pour MaxOS (F5 pour y accéder).

CONTEXTE : OS bare metal x86 32-bit.
RÈGLES : C pur, pas malloc/printf/stdlib.

Fonctionnalités :
- Chiffres 0-9 au clavier
- Opérations + - * /
- Entrée = calculer
- Echap = effacer
- Affichage grand et lisible style Win11

FORMAT :
=== FILE: apps/calculator.h ===
[code complet]
=== END FILE ===

=== FILE: apps/calculator.c ===
[code complet]
=== END FILE ==="""
    },
]

# ══════════════════════════════
# RUN TASK
# ══════════════════════════════
def run_task(task, context, num, total):
    name  = task["name"]
    ttype = task["type"]

    print(f"\n{'='*55}")
    print(f" [{num}/{total}] {name}")
    print(f"{'='*55}")

    d_prog(f"[{num}/{total}] {name}", "Gemini analyse...")

    prompt = f"""Tu es un expert OS bare metal x86. Voici le code de MaxOS :

{context}

{task['prompt']}"""

    t0       = time.time()
    response = gemini_ask(prompt)
    elapsed  = time.time() - t0

    if not response:
        d_err(name, "Gemini n'a pas répondu.")
        return False

    print(f"[Gemini] {len(response)} chars en {elapsed:.1f}s")

    # Analyse JSON
    if ttype == "analyse":
        try:
            start = response.find("{")
            end   = response.rfind("}") + 1
            if start >= 0:
                data = json.loads(response[start:end])
                d_info(
                    "📊 Rapport MaxOS",
                    f"Score: **{data.get('score','?')}/100** — {data.get('commentaire','')}",
                    [
                        {"name": "Bugs", "value": "\n".join(data.get("bugs",[])[:3]) or "Aucun", "inline": True},
                        {"name": "Idées", "value": "\n".join(data.get("ameliorations",[])[:3]), "inline": True},
                    ]
                )
            else:
                d_info("Analyse", response[:600])
        except Exception as ex:
            print(f"[JSON] {ex}")
            d_info("Analyse", response[:600])
        return True

    # Code
    files = parse_files(response)
    if not files:
        d_err(name, f"Aucun fichier détecté.\n```\n{response[:400]}\n```")
        return False

    print(f"[Parser] {len(files)} fichier(s): {list(files.keys())}")

    # Backup + écriture
    backs   = backup_files(list(files.keys()))
    written = write_files(files)

    if not written:
        d_err(name, "Aucun fichier écrit.")
        return False

    # Build
    print("[Build] Compilation...")
    build_ok, log = make_build()

    if build_ok:
        pushed = commit_push(f"feat(ai): {name} [Gemini {GEMINI_MODEL}]")
        if pushed:
            d_ok(
                name,
                f"Amélioration poussée sur GitHub !",
                [
                    {"name": "Fichiers", "value": "\n".join(written), "inline": False},
                    {"name": "Durée",   "value": f"{elapsed:.1f}s",  "inline": True},
                    {"name": "Build",   "value": "✅ OK",             "inline": True},
                ]
            )
            return True
        d_err(name, "Push échoué.")
        return False
    else:
        # Restaurer
        print("[Build] ❌ Restauration...")
        restore_files(backs)
        for path in written:
            if path not in backs:
                full = os.path.join(REPO_PATH, path)
                if os.path.exists(full):
                    os.remove(full)
        d_err(name, f"Build échoué, code restauré.\n```\n{log[-500:]}\n```")
        return False

# ══════════════════════════════
# MAIN
# ══════════════════════════════
def main():
    print("╔══════════════════════════════════════════╗")
    print("║   MaxOS AI Developer v3.0                ║")
    print("║   Multi-model Gemini + Discord fix       ║")
    print("╚══════════════════════════════════════════╝")

    d_info(
        "MaxOS AI v3.0 démarré",
        f"**{len(TASKS)} tâches** planifiées",
        [{"name": "Heure", "value": datetime.now().strftime("%H:%M:%S"), "inline": True}]
    )

    sources = read_sources()
    context = build_context(sources)
    print(f"[Sources] {len(sources)} fichiers, {len(context)} chars")

    success = 0
    for i, task in enumerate(TASKS, 1):
        try:
            if run_task(task, context, i, len(TASKS)):
                success += 1
                sources = read_sources()
                context = build_context(sources)
            if i < len(TASKS):
                print(f"[Pause] 20s...")
                time.sleep(20)
        except KeyboardInterrupt:
            d_info("Arrêt", "Arrêté manuellement.")
            sys.exit(0)
        except Exception as ex:
            print(f"[Erreur] {ex}")
            d_err(f"Erreur tâche {i}", str(ex))

    discord_send(
        f"🏁 Cycle terminé : {success}/{len(TASKS)}",
        f"**{success} réussies** sur {len(TASKS)}",
        0x00FF00 if success == len(TASKS) else 0xFFAA00
    )
    print(f"\n[Fin] {success}/{len(TASKS)} réussies.")

if __name__ == "__main__":
    main()
