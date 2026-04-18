#!/usr/bin/env python3
"""
MaxOS AI Developer
Utilise Gemini pour améliorer MaxOS automatiquement
"""

import os
import sys
import json
import time
import subprocess
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime

# ══════════════════════════════════════════
# CONFIG - Mets tes vraies valeurs ici
# ══════════════════════════════════════════
GEMINI_API_KEY  = "TA_CLE_GEMINI_ICI"
DISCORD_WEBHOOK = "TON_NOUVEAU_WEBHOOK_ICI"  # Après avoir recréé !
REPO_PATH       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEMINI_URL      = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-2.0-flash:generateContent"
    "?key=" + GEMINI_API_KEY
)

# Fichiers à lire pour le contexte
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
    "kernel/kernel_entry.asm",
    "Makefile",
    "linker.ld",
]

# ══════════════════════════════════════════
# DISCORD
# ══════════════════════════════════════════
def discord_send(title, message, color=0x0099FF, fields=None):
    """Envoie une notification Discord."""
    embed = {
        "title": title,
        "description": message,
        "color": color,
        "timestamp": datetime.utcnow().isoformat(),
        "footer": {"text": "MaxOS AI Developer"},
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
        print(f"[Discord] Notification envoyée : {title}")
    except Exception as e:
        print(f"[Discord] Erreur : {e}")

def discord_success(title, msg, fields=None):
    discord_send(f"✅ {title}", msg, 0x00FF00, fields)

def discord_error(title, msg):
    discord_send(f"❌ {title}", msg, 0xFF0000)

def discord_info(title, msg, fields=None):
    discord_send(f"ℹ️ {title}", msg, 0x0099FF, fields)

def discord_progress(title, msg):
    discord_send(f"⚙️ {title}", msg, 0xFFAA00)

# ══════════════════════════════════════════
# LIRE LE CODE SOURCE
# ══════════════════════════════════════════
def read_sources():
    """Lit tous les fichiers sources."""
    sources = {}
    for f in SOURCE_FILES:
        path = os.path.join(REPO_PATH, f)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                sources[f] = fh.read()
        else:
            sources[f] = ""
    return sources

def build_context(sources):
    """Construit le contexte complet pour Gemini."""
    ctx = "=== CODE SOURCE DE MAXOS ===\n\n"
    for fname, content in sources.items():
        if content:
            ctx += f"--- FICHIER: {fname} ---\n"
            ctx += content
            ctx += "\n\n"
    return ctx

# ══════════════════════════════════════════
# GEMINI API
# ══════════════════════════════════════════
def gemini_ask(prompt, max_tokens=8192):
    """Envoie une requête à Gemini."""
    payload = json.dumps({
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.3,
        }
    }).encode("utf-8")

    req = urllib.request.Request(
        GEMINI_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[Gemini] HTTP Error {e.code}: {body}")
        return None
    except Exception as e:
        print(f"[Gemini] Erreur : {e}")
        return None

# ══════════════════════════════════════════
# GIT
# ══════════════════════════════════════════
def git_run(args):
    """Exécute une commande git."""
    result = subprocess.run(
        ["git"] + args,
        cwd=REPO_PATH,
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout, result.stderr

def git_status():
    ok, out, _ = git_run(["status", "--porcelain"])
    return out.strip()

def git_commit_push(message):
    """Add, commit et push."""
    git_run(["add", "-A"])
    ok, out, err = git_run(["commit", "-m", message])
    if not ok:
        print(f"[Git] Commit échoué : {err}")
        return False
    ok, out, err = git_run(["push"])
    if not ok:
        print(f"[Git] Push échoué : {err}")
        return False
    return True

def make_build():
    """Compile MaxOS."""
    result = subprocess.run(
        ["make", "clean", "&&", "make"],
        cwd=REPO_PATH,
        capture_output=True,
        text=True,
        shell=False
    )
    # make clean puis make séparément
    r1 = subprocess.run(["make", "clean"], cwd=REPO_PATH,
                        capture_output=True, text=True)
    r2 = subprocess.run(["make"], cwd=REPO_PATH,
                        capture_output=True, text=True)
    success = r2.returncode == 0
    return success, r2.stdout + r2.stderr

# ══════════════════════════════════════════
# PARSER LA RÉPONSE DE GEMINI
# ══════════════════════════════════════════
def parse_files(response):
    """
    Extrait les fichiers de la réponse Gemini.
    Format attendu :
    === FILE: chemin/fichier.c ===
    [contenu]
    === END FILE ===
    """
    files = {}
    lines = response.split("\n")
    current_file = None
    current_content = []
    in_file = False

    for line in lines:
        if line.startswith("=== FILE:") and line.strip().endswith("==="):
            # Nouveau fichier
            fname = line.replace("=== FILE:", "").replace("===", "").strip()
            current_file = fname
            current_content = []
            in_file = True
        elif line.strip() == "=== END FILE ===" and in_file:
            if current_file:
                files[current_file] = "\n".join(current_content)
            current_file = None
            current_content = []
            in_file = False
        elif in_file:
            current_content.append(line)

    return files

def write_files(files):
    """Écrit les fichiers sur le disque."""
    written = []
    for path, content in files.items():
        full_path = os.path.join(REPO_PATH, path)
        # Créer le dossier si nécessaire
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        written.append(path)
        print(f"[Files] Écrit : {path}")
    return written

# ══════════════════════════════════════════
# TÂCHES D'AMÉLIORATION
# ══════════════════════════════════════════

TASKS = [
    {
        "name": "Analyse et rapport",
        "prompt_suffix": """
Analyse le code de MaxOS et réponds en JSON :
{
  "score_global": 0-100,
  "points_forts": ["..."],
  "points_faibles": ["..."],
  "bugs_detectes": ["..."],
  "priorites": ["amélioration 1", "amélioration 2", "..."]
}
Ne génère PAS de code, juste l'analyse JSON.
"""
    },
    {
        "name": "Amélioration Interface UI",
        "prompt_suffix": """
Améliore UNIQUEMENT les fichiers ui/ui.c et ui/ui.h de MaxOS.

CONTRAINTES ABSOLUES :
- C pur, pas de librairies externes
- Tourne sur x86 32-bit bare metal
- VGA texte 80x25, 16 couleurs uniquement
- Pas de malloc, pas de printf, pas de stdlib
- Interface style Windows 11 (propre, moderne)
- Barres topbar et taskbar plus belles
- Ajoute des icônes ASCII artistiques

Réponds UNIQUEMENT avec les fichiers dans ce format exact :
=== FILE: ui/ui.h ===
[contenu complet du fichier]
=== END FILE ===

=== FILE: ui/ui.c ===
[contenu complet du fichier]
=== END FILE ===
"""
    },
    {
        "name": "Amélioration Bloc-Notes",
        "prompt_suffix": """
Améliore UNIQUEMENT apps/notepad.c et apps/notepad.h.

CONTRAINTES :
- C pur bare metal x86 32-bit
- Ajoute : sélection de texte, recherche simple
- Améliore le rendu visuel
- Curseur plus visible
- Scrolling si le texte dépasse

Format de réponse :
=== FILE: apps/notepad.h ===
[contenu]
=== END FILE ===

=== FILE: apps/notepad.c ===
[contenu]
=== END FILE ===
"""
    },
    {
        "name": "Amélioration Terminal",
        "prompt_suffix": """
Améliore UNIQUEMENT apps/terminal.c et apps/terminal.h.

CONTRAINTES :
- C pur bare metal x86 32-bit
- Ajoute plus de commandes : cat, pwd, whoami, ps, top
- Historique des commandes (flèche haut/bas)
- Autocomplétion basique avec TAB
- Meilleur rendu visuel

Format :
=== FILE: apps/terminal.h ===
[contenu]
=== END FILE ===

=== FILE: apps/terminal.c ===
[contenu]
=== END FILE ===
"""
    },
    {
        "name": "Nouvelle App - Calculatrice",
        "prompt_suffix": """
Crée une nouvelle application calculatrice pour MaxOS.

CONTRAINTES :
- C pur bare metal x86 32-bit
- Opérations : + - * /
- Interface style calculatrice Windows
- Intègre dans le système d'apps existant

Crée ces fichiers :
=== FILE: apps/calculator.h ===
[contenu]
=== END FILE ===

=== FILE: apps/calculator.c ===
[contenu]
=== END FILE ===

Et modifie kernel/kernel.c pour ajouter l'app (F5).
"""
    },
    {
        "name": "Optimisation Clavier",
        "prompt_suffix": """
Améliore UNIQUEMENT drivers/keyboard.c et drivers/keyboard.h.

CONTRAINTES :
- AZERTY parfait
- Tous les caractères spéciaux français
- F1-F12 tous fonctionnels
- Ctrl+C, Ctrl+V, Ctrl+Z gérés
- Alt Gr pour @, #, { } [ ] etc.

Format :
=== FILE: drivers/keyboard.h ===
[contenu]
=== END FILE ===

=== FILE: drivers/keyboard.c ===
[contenu]
=== END FILE ===
"""
    },
    {
        "name": "Nouvelle App - Horloge",
        "prompt_suffix": """
Crée une app horloge/calendrier pour MaxOS.

CONTRAINTES :
- C pur bare metal
- Affiche l'heure en grand (ASCII art)
- Calendrier du mois
- Minuteur simple

Fichiers :
=== FILE: apps/clock.h ===
[contenu]
=== END FILE ===

=== FILE: apps/clock.c ===
[contenu]
=== END FILE ===
"""
    },
]

# ══════════════════════════════════════════
# BOUCLE PRINCIPALE
# ══════════════════════════════════════════
def run_task(task, context, task_num, total):
    """Exécute une tâche d'amélioration."""
    name = task["name"]
    print(f"\n{'='*50}")
    print(f"[{task_num}/{total}] Tâche : {name}")
    print(f"{'='*50}")

    discord_progress(
        f"Tâche {task_num}/{total}",
        f"**{name}**\nGemini analyse et génère des améliorations..."
    )

    # Construire le prompt
    prompt = f"""Tu es un expert en développement d'OS bare metal x86.
Tu travailles sur MaxOS, un système d'exploitation éducatif.

{context}

{task['prompt_suffix']}

RÈGLES IMPORTANTES :
1. Code C pur, AUCUNE librairie externe
2. Compatible x86 32-bit Protected Mode
3. VGA texte 80x25
4. Pas de malloc/free/printf
5. Code complet et fonctionnel
6. Commentaires en français
"""

    # Appel Gemini
    t0 = time.time()
    response = gemini_ask(prompt)
    elapsed = time.time() - t0

    if not response:
        discord_error(name, "Gemini n'a pas répondu.")
        return False

    print(f"[Gemini] Réponse reçue en {elapsed:.1f}s ({len(response)} chars)")

    # Cas spécial : analyse JSON
    if "Analyse" in name:
        try:
            # Extraire le JSON de la réponse
            start = response.find("{")
            end   = response.rfind("}") + 1
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
                fields = [
                    {"name": "Score", "value": str(data.get("score_global", "?")), "inline": True},
                    {"name": "Bugs détectés", "value": str(len(data.get("bugs_detectes", []))), "inline": True},
                    {"name": "Priorités", "value": "\n".join(data.get("priorites", [])[:3]), "inline": False},
                ]
                discord_info("📊 Rapport d'analyse MaxOS",
                            f"Score global : **{data.get('score_global', '?')}/100**",
                            fields)
        except Exception as e:
            discord_info("Analyse", response[:500])
        return True

    # Parser les fichiers
    files = parse_files(response)
    if not files:
        discord_error(name, f"Aucun fichier généré.\nRéponse : {response[:300]}")
        return False

    print(f"[Parser] {len(files)} fichier(s) trouvé(s) : {list(files.keys())}")

    # Écrire les fichiers
    written = write_files(files)

    # Compiler pour vérifier
    print("[Build] Compilation en cours...")
    build_ok, build_log = make_build()

    if build_ok:
        # Commit et push
        msg = f"feat(ai): {name} [Gemini auto-improvement]"
        push_ok = git_commit_push(msg)

        if push_ok:
            discord_success(
                name,
                f"Amélioration appliquée et poussée sur GitHub !",
                [
                    {"name": "Fichiers modifiés", "value": "\n".join(written), "inline": False},
                    {"name": "Temps Gemini", "value": f"{elapsed:.1f}s", "inline": True},
                    {"name": "Build", "value": "✅ Succès", "inline": True},
                ]
            )
            return True
        else:
            discord_error(name, "Push échoué mais build OK.")
            return False
    else:
        # La compilation a échoué, on annule les changements
        git_run(["checkout", "--", "."])
        discord_error(
            name,
            f"Compilation échouée ! Modifications annulées.\n```\n{build_log[-500:]}\n```"
        )
        return False

def main():
    print("╔══════════════════════════════════════╗")
    print("║     MaxOS AI Developer v1.0          ║")
    print("║     Powered by Gemini 2.0 Flash      ║")
    print("╚══════════════════════════════════════╝")

    discord_info(
        "MaxOS AI Developer démarré",
        f"Démarrage du cycle d'amélioration automatique.\n"
        f"**{len(TASKS)} tâches** planifiées.\n"
        f"Repo : {REPO_PATH}",
        [{"name": "Heure", "value": datetime.now().strftime("%H:%M:%S"), "inline": True}]
    )

    # Lire le code source
    print("\n[Sources] Lecture du code...")
    sources = read_sources()
    context = build_context(sources)
    print(f"[Sources] {len(sources)} fichiers, {len(context)} caractères de contexte")

    # Exécuter toutes les tâches
    success_count = 0
    total = len(TASKS)

    for i, task in enumerate(TASKS, 1):
        try:
            ok = run_task(task, context, i, total)
            if ok:
                success_count += 1
                # Relire les sources après modification
                sources = read_sources()
                context = build_context(sources)
            # Pause entre requêtes pour respecter les rate limits
            if i < total:
                print(f"[Rate Limit] Pause 5s...")
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n[!] Interrompu par l'utilisateur")
            discord_info("Arrêt", "Le développeur AI a été arrêté manuellement.")
            sys.exit(0)
        except Exception as e:
            print(f"[Erreur] Tâche {i} : {e}")
            discord_error(f"Erreur tâche {i}", str(e))

    # Rapport final
    discord_success(
        "Cycle terminé !",
        f"**{success_count}/{total}** tâches réussies.",
        [
            {"name": "Succès", "value": str(success_count), "inline": True},
            {"name": "Échecs", "value": str(total - success_count), "inline": True},
            {"name": "Prochain cycle", "value": "Dans 1 heure", "inline": True},
        ]
    )

    print(f"\n[Terminé] {success_count}/{total} tâches réussies.")

if __name__ == "__main__":
    main()
