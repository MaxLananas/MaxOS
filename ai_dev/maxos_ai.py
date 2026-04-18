#!/usr/bin/env python3
"""MaxOS AI Developer v5.0 - Autonome et intelligent"""

import os, sys, json, time, subprocess
import urllib.request, urllib.error
from datetime import datetime

# ══════════════════════════════════════════
GEMINI_API_KEY  = os.environ.get("GEMINI_API_KEY", "")
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")
REPO_PATH       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

print(f"[Config] Gemini : {'OK (' + str(len(GEMINI_API_KEY)) + ' chars)' if GEMINI_API_KEY else 'MANQUANTE!'}")
print(f"[Config] Discord: {'OK' if DISCORD_WEBHOOK else 'MANQUANT!'}")
print(f"[Config] Repo   : {REPO_PATH}")

if not GEMINI_API_KEY:
    print("FATAL: GEMINI_API_KEY manquante!")
    sys.exit(1)

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

# ══════════════════════════════════════════
# DISCORD
# ══════════════════════════════════════════
def discord(title, msg, color=0x5865F2, fields=None):
    if not DISCORD_WEBHOOK:
        print(f"[Discord] Skip: {title}")
        return
    embed = {
        "title": str(title)[:256],
        "description": str(msg)[:2000],
        "color": color,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "footer": {"text": f"MaxOS AI v5.0 | {WORKING_MODEL or 'init'}"},
        "fields": (fields or [])[:10]
    }
    payload = json.dumps({
        "username": "MaxOS AI Bot",
        "embeds": [embed]
    }).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WEBHOOK, data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "DiscordBot (MaxOS, 5.0)",
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"[Discord] OK ({r.status}): {title}")
    except urllib.error.HTTPError as e:
        print(f"[Discord] HTTP {e.code}: {e.read().decode()[:200]}")
    except Exception as e:
        print(f"[Discord] Err: {e}")

def d_ok(t,m,f=None):   discord(f"✅ {t}",m,0x00FF00,f)
def d_err(t,m):          discord(f"❌ {t}",m,0xFF0000)
def d_info(t,m,f=None):  discord(f"ℹ️ {t}",m,0x5865F2,f)
def d_prog(t,m):         discord(f"⚙️ {t}",m,0xFFA500)

# ══════════════════════════════════════════
# GEMINI
# ══════════════════════════════════════════
def find_model():
    global WORKING_MODEL, WORKING_URL
    print("\n[Gemini] Recherche modèle...")
    for model in MODELS:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            + model + ":generateContent?key=" + GEMINI_API_KEY
        )
        payload = json.dumps({
            "contents": [{"parts": [{"text": "Réponds uniquement: READY"}]}],
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
                print(f"[Gemini] ✅ {model} OK: {txt.strip()}")
                WORKING_MODEL = model
                WORKING_URL   = url
                return True
        except urllib.error.HTTPError as e:
            print(f"[Gemini] ❌ {model}: HTTP {e.code}")
            time.sleep(2)
        except Exception as e:
            print(f"[Gemini] ❌ {model}: {e}")
            time.sleep(2)
    return False

def gemini_call(prompt, retries=3):
    global WORKING_URL, WORKING_MODEL
    if not WORKING_URL:
        if not find_model():
            return None

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 65536,
            "temperature": 0.1,
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
                data = json.loads(r.read().decode())
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"[Gemini] ✅ {len(text)} chars")
                return text
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"[Gemini] HTTP {e.code} tentative {attempt}/{retries}")
            if e.code == 429:
                wait = 70 * attempt
                print(f"[Gemini] Rate limit, attente {wait}s...")
                time.sleep(wait)
            elif e.code in (404, 400):
                print(f"[Gemini] Modèle KO, recherche alternative...")
                WORKING_URL = None
                if not find_model():
                    return None
            else:
                print(f"[Gemini] Err: {body[:300]}")
                time.sleep(20)
        except Exception as e:
            print(f"[Gemini] Exception: {e}")
            time.sleep(15)
    return None

# ══════════════════════════════════════════
# FICHIERS
# ══════════════════════════════════════════
def read_all():
    """Lit TOUS les fichiers, intégralement."""
    sources = {}
    for f in ALL_FILES:
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                sources[f] = fh.read()
        else:
            sources[f] = ""  # Fichier manquant
    return sources

def build_full_context(sources):
    """Contexte complet avec TOUS les fichiers."""
    ctx  = "=== CODE COMPLET DE MAXOS ===\n\n"
    ctx += "STRUCTURE DU PROJET :\n"
    for f in ALL_FILES:
        exists = "✓" if sources.get(f) else "✗ MANQUANT"
        ctx += f"  {exists} {f}\n"
    ctx += "\n"

    for f, content in sources.items():
        ctx += f"{'='*60}\n"
        ctx += f"FICHIER: {f}\n"
        ctx += f"{'='*60}\n"
        if content:
            ctx += content
        else:
            ctx += "[FICHIER VIDE OU MANQUANT]\n"
        ctx += "\n\n"
    return ctx

def parse_files(response):
    """
    Parse robuste qui gère plusieurs formats :
    === FILE: path ===
    === END FILE ===
    """
    files = {}

    # Format principal
    lines     = response.split("\n")
    cur_file  = None
    cur_lines = []
    in_file   = False

    for line in lines:
        stripped = line.strip()

        # Détecter début
        if "=== FILE:" in stripped and stripped.endswith("==="):
            # Extraire le chemin
            start = stripped.index("=== FILE:") + 9
            end   = stripped.rindex("===")
            fname = stripped[start:end].strip()
            # Nettoyer les backticks
            fname = fname.strip("`").strip()
            cur_file  = fname
            cur_lines = []
            in_file   = True
            continue

        # Détecter fin
        if stripped == "=== END FILE ===" and in_file:
            if cur_file:
                content = "\n".join(cur_lines)
                # Nettoyer blocs markdown
                content = content.strip()
                for lang in ["```c", "```asm", "```makefile", "```", "```nasm"]:
                    if content.startswith(lang):
                        content = "\n".join(content.split("\n")[1:])
                        break
                if content.endswith("```"):
                    content = "\n".join(content.split("\n")[:-1])
                files[cur_file] = content.strip()
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
        # Sécurité
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
    print(f"[Restore] {len(backups)} fichier(s) restauré(s)")

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
    ok, _, e = git(["commit", "-m", msg])
    if not ok:
        if "nothing to commit" in e:
            print("[Git] Rien à committer")
            return True
        print(f"[Git] Commit KO: {e[:200]}")
        return False
    ok2, _, e2 = git(["push"])
    if not ok2:
        print(f"[Git] Push KO: {e2[:200]}")
        return False
    print(f"[Git] ✅ Pushé: {msg}")
    return True

def make_build():
    subprocess.run(["make", "clean"], cwd=REPO_PATH, capture_output=True)
    r = subprocess.run(
        ["make"], cwd=REPO_PATH,
        capture_output=True, text=True
    )
    success = r.returncode == 0
    log     = r.stdout + r.stderr
    print(f"[Build] {'✅ OK' if success else '❌ ÉCHEC'}")
    if not success:
        # Afficher les erreurs importantes
        for line in log.split("\n"):
            if "error:" in line or "Error" in line:
                print(f"[Build] {line}")
    return success, log

# ══════════════════════════════════════════
# PHASE 1 : GEMINI ANALYSE ET DÉCIDE
# ══════════════════════════════════════════
def phase_analyse(context):
    """
    Gemini analyse le code et décide lui-même
    ce qu'il veut faire.
    """
    print("\n[Phase 1] Gemini analyse le code...")

    prompt = f"""Tu es un expert en développement d'OS bare metal x86.
Tu dois analyser le code de MaxOS et décider toi-même ce que tu veux améliorer.

{context}

INFORMATIONS SUR L'ENVIRONNEMENT :
- Compilateur: gcc -m32 -ffreestanding -fno-stack-protector -fno-builtin -fno-pic -fno-pie -nostdlib -nostdinc -w -c
- Assembleur: nasm -f elf (pour .o) et nasm -f bin (pour boot.bin)
- Linker: ld -m elf_i386 -T linker.ld --oformat binary
- VGA texte: 80 colonnes x 25 lignes, 16 couleurs
- Mémoire: Kernel à 0x8000, Stack à 0x90000, VGA à 0xB8000
- PAS de librairies (pas malloc, printf, stdlib, string.h, etc.)

ANALYSE CE CODE ET RÉPONDS EN JSON UNIQUEMENT :
{{
  "score_actuel": 0-100,
  "problemes_critiques": [
    {{"fichier": "path/fichier.c", "ligne_approx": 42, "description": "problème précis"}}
  ],
  "fichiers_manquants": ["path/fichier.c"],
  "plan_ameliorations": [
    {{
      "nom": "Nom de l'amélioration",
      "priorite": "CRITIQUE|HAUTE|NORMALE",
      "fichiers_a_modifier": ["path/fichier.h", "path/fichier.c"],
      "fichiers_a_creer": ["path/nouveau.h", "path/nouveau.c"],
      "description": "Ce que tu vas faire exactement"
    }}
  ],
  "commentaire_global": "Ton analyse en une phrase"
}}

Sois honnête et précis. Identifie les vrais problèmes de compilation et d'architecture.
Réponds UNIQUEMENT avec le JSON valide, aucun texte avant ou après."""

    response = gemini_call(prompt)
    if not response:
        return None

    try:
        # Extraire JSON
        i = response.find("{")
        j = response.rfind("}") + 1
        if i >= 0 and j > i:
            data = json.loads(response[i:j])
            return data
    except Exception as e:
        print(f"[Analyse] Erreur JSON: {e}")
        print(f"[Analyse] Réponse: {response[:500]}")

    return None

# ══════════════════════════════════════════
# PHASE 2 : GEMINI IMPLÉMENTE
# ══════════════════════════════════════════
def phase_implement(context, amelioration, all_sources):
    """
    Gemini implémente UNE amélioration avec le code complet.
    """
    nom        = amelioration.get("nom", "Amélioration")
    fichiers_m = amelioration.get("fichiers_a_modifier", [])
    fichiers_c = amelioration.get("fichiers_a_creer", [])
    desc       = amelioration.get("description", "")
    tous_fich  = fichiers_m + fichiers_c

    print(f"\n[Impl] {nom}")
    print(f"[Impl] Fichiers: {tous_fich}")

    # Construire le contexte SPÉCIFIQUE aux fichiers concernés
    # + les fichiers liés (headers, etc.)
    fichiers_lies = set(tous_fich)

    # Ajouter les fichiers liés automatiquement
    for f in tous_fich:
        base = f.replace(".c", "").replace(".h", "")
        for ext in [".c", ".h"]:
            candidate = base + ext
            if candidate in all_sources:
                fichiers_lies.add(candidate)

    # Toujours inclure kernel.c et les headers principaux
    fichiers_lies.update([
        "kernel/kernel.c",
        "drivers/screen.h",
        "drivers/keyboard.h",
        "ui/ui.h",
        "Makefile",
        "linker.ld",
    ])

    # Contexte ciblé
    ctx_cible = "=== FICHIERS CONCERNÉS ===\n\n"
    for f in sorted(fichiers_lies):
        content = all_sources.get(f, "")
        ctx_cible += f"--- {f} ---\n"
        ctx_cible += (content if content else "[FICHIER MANQUANT - À CRÉER]\n")
        ctx_cible += "\n\n"

    # Contexte des autres fichiers (résumé)
    ctx_autres  = "\n=== AUTRES FICHIERS (résumé) ===\n"
    for f, c in all_sources.items():
        if f not in fichiers_lies and c:
            ctx_autres += f"[{f}]: {len(c)} chars\n"

    prompt = f"""Tu es un expert OS bare metal x86. Tu travailles sur MaxOS.

TÂCHE : {nom}
DESCRIPTION : {desc}

FICHIERS À MODIFIER : {fichiers_m}
FICHIERS À CRÉER    : {fichiers_c}

{ctx_cible}

{ctx_autres}

CONTRAINTES ABSOLUES :
1. C pur UNIQUEMENT - ZÉRO include de librairie standard
2. Pas de malloc, free, printf, sprintf, strlen, strcpy, memset, memcpy
3. Pas de #include <stdio.h>, <stdlib.h>, <string.h>, etc.
4. Compatible gcc -m32 -ffreestanding -fno-pic -fno-pie -nostdlib -nostdinc
5. VGA texte 80x25, 16 couleurs, adresse 0xB8000
6. Assembly NASM uniquement
7. Si tu modifies kernel.c, inclut le fichier COMPLET
8. Si tu crées un nouveau fichier .c, il doit être ajouté au Makefile

INSTRUCTIONS IMPORTANTES :
- Fournis le code COMPLET de chaque fichier (pas de "..." ni de [reste inchangé])
- Chaque fichier doit compiler sans erreur
- Respecte les signatures des fonctions existantes
- Si tu ajoutes une fonction dans un .c, déclare-la dans le .h correspondant
- Si tu crées apps/calculator.c, modifie aussi kernel/kernel.c pour l'intégrer

FORMAT DE RÉPONSE OBLIGATOIRE :
Tu dois répondre UNIQUEMENT avec les fichiers dans ce format exact.
PAS de texte d'introduction. PAS d'explication avant les fichiers.
Commence DIRECTEMENT par le premier === FILE: ===

=== FILE: chemin/fichier.h ===
[contenu complet]
=== END FILE ===

=== FILE: chemin/fichier.c ===
[contenu complet]
=== END FILE ===

Commence maintenant avec le premier fichier."""

    t0       = time.time()
    response = gemini_call(prompt)
    elapsed  = time.time() - t0

    if not response:
        d_err(nom, "Gemini n'a pas répondu.")
        return False, []

    print(f"[Impl] Réponse: {len(response)} chars en {elapsed:.1f}s")

    # Parser
    files = parse_files(response)
    print(f"[Impl] Fichiers parsés: {list(files.keys())}")

    if not files:
        # Debug : afficher le début de la réponse
        print(f"[Debug] Début réponse:\n{response[:800]}")
        d_err(nom, f"Aucun fichier trouvé.\nDébut:\n```\n{response[:600]}\n```")
        return False, []

    # Backup + écriture
    backs   = backup_files(list(files.keys()))
    written = write_files(files)

    if not written:
        d_err(nom, "Aucun fichier écrit.")
        return False, []

    # Build
    build_ok, log = make_build()

    if build_ok:
        pushed = git_push(f"feat(ai): {nom} [{WORKING_MODEL}]")
        if pushed:
            d_ok(
                nom,
                f"Amélioration appliquée avec succès !",
                [
                    {"name": "📁 Fichiers modifiés", "value": "\n".join(written), "inline": False},
                    {"name": "⏱️ Durée",  "value": f"{elapsed:.1f}s",    "inline": True},
                    {"name": "🤖 Modèle", "value": WORKING_MODEL or "?", "inline": True},
                ]
            )
            return True, written
        d_err(nom, "Push Git échoué.")
        restore_files(backs)
        return False, []
    else:
        # Essayer de corriger automatiquement
        print("[Build] Tentative de correction automatique...")
        fixed = try_fix_build(log, files, backs, context)
        if fixed:
            return True, written

        restore_files(backs)
        # Supprimer les nouveaux fichiers
        for p in written:
            if p not in backs:
                fp = os.path.join(REPO_PATH, p)
                if os.path.exists(fp):
                    os.remove(fp)

        d_err(nom, f"Build échoué, code restauré.\n```\n{log[-800:]}\n```")
        return False, []

# ══════════════════════════════════════════
# AUTO-FIX DES ERREURS DE COMPILATION
# ══════════════════════════════════════════
def try_fix_build(build_log, generated_files, backups, context):
    """Demande à Gemini de corriger les erreurs."""
    print("[Fix] Demande correction à Gemini...")

    # Lire les fichiers actuels (potentiellement cassés)
    current = {}
    for p in generated_files:
        fp = os.path.join(REPO_PATH, p)
        if os.path.exists(fp):
            with open(fp, "r") as f:
                current[p] = f.read()

    ctx_files = ""
    for p, c in current.items():
        ctx_files += f"--- {p} ---\n{c}\n\n"

    prompt = f"""Tu as généré du code pour MaxOS mais la compilation a échoué.

ERREURS DE COMPILATION :
{build_log[-2000:]}

FICHIERS QUE TU AS GÉNÉRÉS :
{ctx_files}

CORRIGE UNIQUEMENT les erreurs de compilation.
RÈGLES : C pur, pas de librairies, gcc -m32 -ffreestanding -nostdlib -nostdinc

Réponds DIRECTEMENT avec les fichiers corrigés (pas de texte avant) :

=== FILE: chemin/fichier.c ===
[contenu corrigé complet]
=== END FILE ==="""

    response = gemini_call(prompt)
    if not response:
        return False

    files = parse_files(response)
    if not files:
        return False

    write_files(files)
    build_ok, log = make_build()

    if build_ok:
        msg = f"fix(ai): Auto-correction build [{WORKING_MODEL}]"
        git_push(msg)
        d_ok("Auto-correction", "Erreurs de compilation corrigées automatiquement !")
        return True

    return False

# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
def main():
    print("╔══════════════════════════════════════════════╗")
    print("║   MaxOS AI Developer v5.0                    ║")
    print("║   Autonome - Gemini décide tout seul         ║")
    print("╚══════════════════════════════════════════════╝\n")

    # Trouver le modèle
    if not find_model():
        print("FATAL: Aucun modèle disponible.")
        d_err("Démarrage échoué", "Aucun modèle Gemini accessible.")
        sys.exit(1)

    d_info(
        "MaxOS AI v5.0 démarré 🚀",
        f"Modèle : **{WORKING_MODEL}**\nGemini va analyser et décider lui-même les améliorations.",
        [{"name": "⏰ Heure", "value": datetime.now().strftime("%H:%M:%S"), "inline": True}]
    )

    # Lire TOUT le code
    print("\n[Sources] Lecture complète du code...")
    sources = read_all()
    context = build_full_context(sources)
    print(f"[Sources] {len(sources)} fichiers, {len(context)} chars total")

    # ── Phase 1 : Analyse et décision ──
    print("\n" + "═"*55)
    print(" PHASE 1 : Gemini analyse et décide")
    print("═"*55)

    analyse = phase_analyse(context)

    if not analyse:
        d_err("Analyse échouée", "Impossible d'analyser le code.")
        sys.exit(1)

    # Afficher le rapport
    score   = analyse.get("score_actuel", "?")
    comment = analyse.get("commentaire_global", "")
    plan    = analyse.get("plan_ameliorations", [])
    manq    = analyse.get("fichiers_manquants", [])
    crit    = analyse.get("problemes_critiques", [])

    print(f"\n[Rapport] Score: {score}/100")
    print(f"[Rapport] {comment}")
    print(f"[Rapport] Fichiers manquants: {manq}")
    print(f"[Rapport] {len(crit)} problème(s) critique(s)")
    print(f"[Rapport] {len(plan)} amélioration(s) planifiée(s)")

    for i, a in enumerate(plan):
        print(f"  [{i+1}] {a.get('priorite','?')} - {a.get('nom','?')}")

    # Bugs détectés dans Discord
    bugs_txt = "\n".join([
        f"• **{b.get('fichier','?')}** : {b.get('description','?')}"
        for b in crit[:5]
    ]) or "Aucun"

    plan_txt = "\n".join([
        f"{i+1}. [{a.get('priorite','?')}] {a.get('nom','?')}"
        for i, a in enumerate(plan[:8])
    ]) or "Aucun"

    d_info(
        f"📊 Analyse MaxOS - Score {score}/100",
        f"_{comment}_",
        [
            {"name": "🐛 Problèmes détectés", "value": bugs_txt, "inline": False},
            {"name": "📋 Plan d'action",       "value": plan_txt, "inline": False},
            {"name": "📁 Fichiers manquants",  "value": "\n".join(manq) or "Aucun", "inline": True},
        ]
    )

    # ── Phase 2 : Implémentation ──
    print("\n" + "═"*55)
    print(" PHASE 2 : Implémentation des améliorations")
    print("═"*55)

    # Trier par priorité
    priority_order = {"CRITIQUE": 0, "HAUTE": 1, "NORMALE": 2}
    plan_sorted = sorted(
        plan,
        key=lambda x: priority_order.get(x.get("priorite", "NORMALE"), 2)
    )

    success_count = 0
    total         = len(plan_sorted)

    for i, amelioration in enumerate(plan_sorted, 1):
        nom      = amelioration.get("nom", f"Amélioration {i}")
        priorite = amelioration.get("priorite", "NORMALE")

        print(f"\n{'═'*55}")
        print(f" [{i}/{total}] [{priorite}] {nom}")
        print(f"{'═'*55}")

        d_prog(
            f"[{i}/{total}] {nom}",
            f"Priorité : **{priorite}**\n{amelioration.get('description','')}"
        )

        # Relire les sources (elles ont peut-être changé)
        sources = read_all()

        ok, written = phase_implement(context, amelioration, sources)
        if ok:
            success_count += 1
            # Mettre à jour le contexte
            sources = read_all()
            context = build_full_context(sources)

        # Pause entre tâches
        if i < total:
            wait = 30
            print(f"[Pause] {wait}s...")
            time.sleep(wait)

    # ── Rapport final ──
    color = 0x00FF00 if success_count == total else 0xFFA500
    discord(
        f"🏁 Cycle terminé : {success_count}/{total}",
        f"MaxOS a reçu **{success_count} améliorations** ce cycle !",
        color,
        [
            {"name": "✅ Succès",  "value": str(success_count),        "inline": True},
            {"name": "❌ Échecs",  "value": str(total-success_count),   "inline": True},
            {"name": "🤖 Modèle", "value": WORKING_MODEL or "?",        "inline": True},
            {"name": "📊 Score initial", "value": f"{score}/100",       "inline": True},
        ]
    )

    print(f"\n[FIN] {success_count}/{total} améliorations réussies.")

if __name__ == "__main__":
    main()
