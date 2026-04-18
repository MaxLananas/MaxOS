#!/usr/bin/env python3
"""
MaxOS AI Developer v2.0
Gemini 1.5 Flash - Gratuit 1500 req/jour
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
import urllib.error
from datetime import datetime

# ══════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════
GEMINI_API_KEY  = "AIzaSyCwJrs7K9ccjW2oxieRkNQ8zfViqyCf3q0"
DISCORD_WEBHOOK = "https://discord.com/api/webhooks/1494873787596800080/sPhaZzBYUtPC_vhUgI94fPGXMMCyMc10-PbUGN62lZWDnurOot8ghD4Mm0Fki9EfZAoo"
REPO_PATH       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ✅ Modèle gratuit qui fonctionne
GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_URL   = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    + GEMINI_MODEL
    + ":generateContent?key="
    + GEMINI_API_KEY
)

SOURCE_FILES = [
    "kernel/kernel.c",
    "drivers/screen.c",
    "drivers/screen.h",
    "drivers/keyboard.c",
    "drivers/keyboard.h",
    "ui/ui.c",
    "ui/ui.h",
    "apps/notepad.c",
    "apps/terminal.c",
    "apps/sysinfo.c",
    "apps/about.c",
    "boot/boot.asm",
    "Makefile",
    "linker.ld",
]

# ══════════════════════════════════════════
# DISCORD
# ══════════════════════════════════════════
def discord_send(title, message, color=0x0099FF, fields=None):
    if not DISCORD_WEBHOOK or "TON_NOUVEAU" in DISCORD_WEBHOOK:
        print(f"[Discord] Skipped (pas de webhook): {title}")
        return

    embed = {
        "title": title,
        "description": str(message)[:2000],
        "color": color,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "footer": {"text": "MaxOS AI Developer v2.0"},
        "fields": fields or []
    }
    payload = json.dumps({"embeds": [embed]}).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WEBHOOK,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        urllib.request.urlopen(req, timeout=10)
        print(f"[Discord] OK: {title}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[Discord] Erreur {e.code}: {body[:200]}")
    except Exception as e:
        print(f"[Discord] Erreur: {e}")

def ok(title, msg, fields=None):
    discord_send(f"✅ {title}", msg, 0x00FF00, fields)

def err(title, msg):
    discord_send(f"❌ {title}", msg, 0xFF0000)

def info(title, msg, fields=None):
    discord_send(f"ℹ️ {title}", msg, 0x0099FF, fields)

def progress(title, msg):
    discord_send(f"⚙️ {title}", msg, 0xFFAA00)

# ══════════════════════════════════════════
# GEMINI
# ══════════════════════════════════════════
def gemini_ask(prompt, retries=3):
    """Appelle Gemini avec retry automatique."""
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
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["candidates"][0]["content"]["parts"][0]["text"]

        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"[Gemini] Erreur {e.code} (tentative {attempt+1}/{retries})")

            if e.code == 429:
                # Rate limit - attendre
                wait = 65 * (attempt + 1)
                print(f"[Gemini] Rate limit, attente {wait}s...")
                time.sleep(wait)
            elif e.code == 400:
                print(f"[Gemini] Erreur 400: {body[:300]}")
                return None
            else:
                print(f"[Gemini] {body[:300]}")
                time.sleep(10)

        except Exception as e:
            print(f"[Gemini] Exception: {e}")
            time.sleep(10)

    return None

# ══════════════════════════════════════════
# SOURCES
# ══════════════════════════════════════════
def read_sources():
    sources = {}
    for f in SOURCE_FILES:
        path = os.path.join(REPO_PATH, f)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                sources[f] = fh.read()
    return sources

def build_context(sources):
    ctx = "=== CODE SOURCE MAXOS ===\n\n"
    for fname, content in sources.items():
        if content:
            # Limiter la taille pour ne pas dépasser les tokens
            content_limited = content[:3000]
            ctx += f"--- {fname} ---\n{content_limited}\n\n"
    return ctx

# ══════════════════════════════════════════
# GIT
# ══════════════════════════════════════════
def git(args):
    r = subprocess.run(
        ["git"] + args,
        cwd=REPO_PATH,
        capture_output=True,
        text=True
    )
    return r.returncode == 0, r.stdout, r.stderr

def commit_push(msg):
    git(["add", "-A"])
    ok_c, _, err_c = git(["commit", "-m", msg])
    if not ok_c:
        if "nothing to commit" in err_c:
            print("[Git] Rien à committer")
            return True
        print(f"[Git] Commit échoué: {err_c}")
        return False
    ok_p, _, err_p = git(["push"])
    if not ok_p:
        print(f"[Git] Push échoué: {err_p}")
        return False
    print(f"[Git] Commit+Push OK: {msg}")
    return True

def make_build():
    subprocess.run(["make", "clean"], cwd=REPO_PATH,
                   capture_output=True)
    r = subprocess.run(["make"], cwd=REPO_PATH,
                       capture_output=True, text=True)
    return r.returncode == 0, r.stdout + r.stderr

# ══════════════════════════════════════════
# PARSER FICHIERS
# ══════════════════════════════════════════
def parse_files(response):
    """Extrait les fichiers de la réponse Gemini."""
    files = {}
    lines = response.split("\n")
    current_file = None
    current_lines = []
    in_file = False

    for line in lines:
        stripped = line.strip()

        # Détecter début fichier
        if stripped.startswith("=== FILE:") and stripped.endswith("==="):
            fname = stripped[9:-3].strip()
            current_file = fname
            current_lines = []
            in_file = True
            continue

        # Détecter fin fichier
        if stripped == "=== END FILE ===" and in_file:
            if current_file:
                # Enlever les blocs ```c et ``` si présents
                content = "\n".join(current_lines)
                content = content.strip()
                if content.startswith("```"):
                    lines2 = content.split("\n")
                    lines2 = lines2[1:]  # Enlever ```c
                    if lines2 and lines2[-1].strip() == "```":
                        lines2 = lines2[:-1]
                    content = "\n".join(lines2)
                files[current_file] = content
            current_file = None
            current_lines = []
            in_file = False
            continue

        if in_file:
            current_lines.append(line)

    return files

def write_files(files):
    written = []
    for path, content in files.items():
        # Sécurité : pas de chemin absolu ou ../
        if path.startswith("/") or ".." in path:
            print(f"[Security] Chemin refusé: {path}")
            continue
        full = os.path.join(REPO_PATH, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        written.append(path)
        print(f"[Write] {path} ({len(content)} chars)")
    return written

# ══════════════════════════════════════════
# TÂCHES
# ══════════════════════════════════════════
TASKS = [
    {
        "name": "Analyse du code",
        "type": "analyse",
        "prompt": """
Analyse ce code d'OS bare metal x86 et donne un rapport JSON :
{
  "score": 0-100,
  "bugs": ["bug 1", "bug 2"],
  "ameliorations": ["idée 1", "idée 2", "idée 3"],
  "complexite": "simple/moyen/complexe",
  "commentaire": "résumé en une phrase"
}
Réponds UNIQUEMENT avec le JSON, rien d'autre.
"""
    },
    {
        "name": "Amélioration UI",
        "type": "code",
        "files": ["ui/ui.h", "ui/ui.c"],
        "prompt": """
Améliore l'interface utilisateur de MaxOS (fichiers ui/ui.h et ui/ui.c).

OBJECTIF : Interface style Windows 11, propre et moderne.

CONTRAINTES ABSOLUES :
- C pur, zéro librairie externe
- x86 32-bit bare metal
- VGA texte 80x25, 16 couleurs max
- Pas de malloc, printf, stdlib
- Le code DOIT compiler avec : gcc -m32 -ffreestanding -fno-pic -fno-pie -nostdlib -nostdinc

AMÉLIORATIONS SOUHAITÉES :
- Topbar plus élégante avec séparateurs
- Taskbar style Win11 avec icônes ASCII
- Meilleure utilisation des couleurs

FORMAT DE RÉPONSE OBLIGATOIRE :
=== FILE: ui/ui.h ===
[contenu complet]
=== END FILE ===

=== FILE: ui/ui.c ===
[contenu complet]
=== END FILE ===
"""
    },
    {
        "name": "Amélioration Terminal",
        "type": "code",
        "files": ["apps/terminal.h", "apps/terminal.c"],
        "prompt": """
Améliore le terminal de MaxOS.

CONTRAINTES :
- C pur bare metal x86 32-bit
- Pas de librairies
- Ajoute ces commandes : pwd, whoami, ps, top, cat, mkdir
- Historique avec flèche haut/bas (20 entrées)
- Meilleur affichage

FORMAT :
=== FILE: apps/terminal.h ===
[contenu complet]
=== END FILE ===

=== FILE: apps/terminal.c ===
[contenu complet]
=== END FILE ===
"""
    },
    {
        "name": "Amélioration Bloc-Notes",
        "type": "code",
        "files": ["apps/notepad.h", "apps/notepad.c"],
        "prompt": """
Améliore le bloc-notes de MaxOS.

CONTRAINTES :
- C pur bare metal x86 32-bit
- Curseur visible et clignotant
- Navigation fluide avec flèches
- Home/End fonctionnels
- Compteur de mots dans la statusbar
- Meilleur rendu visuel

FORMAT :
=== FILE: apps/notepad.h ===
[contenu complet]
=== END FILE ===

=== FILE: apps/notepad.c ===
[contenu complet]
=== END FILE ===
"""
    },
    {
        "name": "Nouvelle App Calculatrice",
        "type": "code",
        "files": ["apps/calculator.h", "apps/calculator.c"],
        "prompt": """
Crée une calculatrice pour MaxOS accessible avec F5.

CONTRAINTES :
- C pur bare metal x86 32-bit
- Opérations : + - * /
- Affichage style calculatrice Windows
- Touches : chiffres, opérateurs, Entrée=calculer, Echap=effacer

CRÉE CES FICHIERS :
=== FILE: apps/calculator.h ===
[contenu complet]
=== END FILE ===

=== FILE: apps/calculator.c ===
[contenu complet]
=== END FILE ===
"""
    },
]

# ══════════════════════════════════════════
# EXÉCUTION TÂCHE
# ══════════════════════════════════════════
def run_task(task, context, num, total):
    name = task["name"]
    ttype = task["type"]

    print(f"\n{'='*55}")
    print(f" [{num}/{total}] {name}")
    print(f"{'='*55}")

    progress(f"[{num}/{total}] {name}", "Gemini travaille...")

    # Construire prompt
    prompt = f"""Tu es un expert OS bare metal x86.
Voici le code source actuel de MaxOS :

{context}

{task['prompt']}
"""

    t0 = time.time()
    response = gemini_ask(prompt)
    elapsed = time.time() - t0

    if not response:
        err(name, "Gemini n'a pas répondu.")
        return False

    print(f"[Gemini] Réponse: {len(response)} chars en {elapsed:.1f}s")

    # Analyse JSON
    if ttype == "analyse":
        try:
            start = response.find("{")
            end   = response.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
                info(
                    f"📊 Rapport MaxOS",
                    f"Score: **{data.get('score', '?')}/100**\n"
                    f"{data.get('commentaire', '')}",
                    [
                        {
                            "name": "Bugs",
                            "value": "\n".join(data.get("bugs", [])[:3]) or "Aucun",
                            "inline": True
                        },
                        {
                            "name": "Améliorations",
                            "value": "\n".join(data.get("ameliorations", [])[:3]),
                            "inline": True
                        }
                    ]
                )
            else:
                info("Analyse", response[:800])
        except Exception as e:
            print(f"[Analyse] Erreur JSON: {e}")
            info("Analyse", response[:500])
        return True

    # Code
    files = parse_files(response)
    if not files:
        err(name, f"Aucun fichier parsé.\nDébut réponse:\n{response[:400]}")
        return False

    print(f"[Parser] {len(files)} fichier(s): {list(files.keys())}")

    # Backup
    backups = {}
    for path in files:
        full = os.path.join(REPO_PATH, path)
        if os.path.exists(full):
            with open(full, "r") as f:
                backups[path] = f.read()

    # Écrire
    written = write_files(files)
    if not written:
        err(name, "Aucun fichier écrit.")
        return False

    # Compiler
    print("[Build] Compilation...")
    build_ok, build_log = make_build()

    if build_ok:
        pushed = commit_push(
            f"feat(ai): {name} - auto-improvement by Gemini"
        )
        if pushed:
            ok(
                name,
                "Amélioration compilée et poussée !",
                [
                    {"name": "Fichiers", "value": "\n".join(written), "inline": False},
                    {"name": "Temps", "value": f"{elapsed:.1f}s", "inline": True},
                    {"name": "Build", "value": "✅", "inline": True},
                ]
            )
            return True
        else:
            err(name, "Push échoué.")
            return False
    else:
        # Restaurer les backups
        print("[Build] Échec ! Restauration...")
        for path, content in backups.items():
            full = os.path.join(REPO_PATH, path)
            with open(full, "w") as f:
                f.write(content)
        # Supprimer les nouveaux fichiers
        for path in written:
            if path not in backups:
                full = os.path.join(REPO_PATH, path)
                if os.path.exists(full):
                    os.remove(full)

        err(
            name,
            f"Compilation échouée. Restauré.\n```\n{build_log[-600:]}\n```"
        )
        return False

# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
def main():
    print("╔══════════════════════════════════════════╗")
    print("║   MaxOS AI Developer v2.0                ║")
    print("║   Gemini 1.5 Flash - Gratuit             ║")
    print("╚══════════════════════════════════════════╝")
    print(f"Repo   : {REPO_PATH}")
    print(f"Modèle : {GEMINI_MODEL}")
    print(f"Tâches : {len(TASKS)}")

    info(
        "MaxOS AI Developer v2.0 démarré",
        f"**{len(TASKS)} tâches** planifiées\nModèle: `{GEMINI_MODEL}`",
        [{"name": "Heure", "value": datetime.now().strftime("%H:%M:%S"), "inline": True}]
    )

    # Lire sources
    sources  = read_sources()
    context  = build_context(sources)
    print(f"[Sources] {len(sources)} fichiers, {len(context)} chars")

    success = 0

    for i, task in enumerate(TASKS, 1):
        try:
            if run_task(task, context, i, len(TASKS)):
                success += 1
                # Relire après modification
                sources = read_sources()
                context = build_context(sources)

            # Pause entre tâches (rate limit)
            if i < len(TASKS):
                wait = 30
                print(f"[Rate Limit] Pause {wait}s...")
                time.sleep(wait)

        except KeyboardInterrupt:
            print("\n[!] Arrêté")
            info("Arrêt", "AI Developer arrêté manuellement.")
            sys.exit(0)
        except Exception as e:
            print(f"[Erreur] {e}")
            err(f"Erreur tâche {i}", str(e))

    # Rapport final
    color = 0x00FF00 if success == len(TASKS) else 0xFFAA00
    discord_send(
        f"🏁 Cycle terminé : {success}/{len(TASKS)}",
        f"**{success} tâches réussies** sur {len(TASKS)}",
        color,
        [
            {"name": "Succès", "value": str(success), "inline": True},
            {"name": "Échecs", "value": str(len(TASKS)-success), "inline": True},
        ]
    )
    print(f"\n[Fin] {success}/{len(TASKS)} tâches réussies.")

if __name__ == "__main__":
    main()
