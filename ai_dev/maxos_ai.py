#!/usr/bin/env python3
"""MaxOS AI Developer v6.0"""

import os, sys, json, time, subprocess
import urllib.request, urllib.error
from datetime import datetime

# ══════════════════════════════════════════
# SÉCURITÉ : Lecture UNIQUEMENT depuis env
# JAMAIS de clé en dur dans le code !
# ══════════════════════════════════════════
GEMINI_API_KEY  = os.environ.get("GEMINI_API_KEY", "")
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")
REPO_PATH       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Validation
if not GEMINI_API_KEY:
    print("FATAL: GEMINI_API_KEY manquante dans les variables d'environnement!")
    print("GitHub: Settings → Secrets → GEMINI_API_KEY")
    sys.exit(1)

# Vérification de sécurité : la clé ne doit PAS apparaître dans les logs
KEY_LEN    = len(GEMINI_API_KEY)
KEY_MASKED = GEMINI_API_KEY[:4] + "*" * (KEY_LEN - 8) + GEMINI_API_KEY[-4:]

print(f"[Security] Clé Gemini  : {KEY_MASKED} ({KEY_LEN} chars)")
print(f"[Security] Discord     : {'OK (' + str(len(DISCORD_WEBHOOK)) + ' chars)' if DISCORD_WEBHOOK else 'ABSENT'}")
print(f"[Config]   Repo        : {REPO_PATH}")
print(f"[Config]   Heure       : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ══════════════════════════════════════════
# MODÈLES GEMINI (ordre de préférence)
# ══════════════════════════════════════════
MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
]

WORKING_MODEL = None
WORKING_URL   = None

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
# DISCORD - Webhooks riches
# ══════════════════════════════════════════
def discord_send(embeds):
    """Envoie un ou plusieurs embeds Discord."""
    if not DISCORD_WEBHOOK:
        return

    payload = json.dumps({
        "username": "MaxOS AI Bot",
        "embeds": embeds[:10]
    }).encode("utf-8")

    req = urllib.request.Request(
        DISCORD_WEBHOOK,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "DiscordBot (MaxOS, 6.0)",
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            status = r.status
            if status not in (200, 204):
                print(f"[Discord] Status inattendu: {status}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[Discord] HTTP {e.code}: {body[:300]}")
    except Exception as e:
        print(f"[Discord] Erreur: {e}")
    return False

def make_embed(title, desc, color, fields=None, image=None, thumbnail=None):
    """Crée un embed Discord riche."""
    embed = {
        "title": str(title)[:256],
        "description": str(desc)[:4096],
        "color": color,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "footer": {
            "text": f"MaxOS AI v6.0  •  {WORKING_MODEL or 'init'}  •  github.com/MaxLananas/MaxOS",
            "icon_url": "https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png"
        },
    }
    if fields:
        embed["fields"] = fields[:25]
    if thumbnail:
        embed["thumbnail"] = {"url": thumbnail}
    return embed

# Raccourcis
def d_start(model, nb_tasks):
    discord_send([make_embed(
        "🚀 MaxOS AI Developer v6.0 démarré",
        f"Gemini va analyser le code et décider lui-même des améliorations.",
        0x5865F2,
        [
            {"name": "🤖 Modèle",   "value": f"`{model}`",                         "inline": True},
            {"name": "📁 Fichiers", "value": str(len(ALL_FILES)),                   "inline": True},
            {"name": "🕐 Heure",    "value": datetime.now().strftime("%H:%M:%S"),   "inline": True},
            {"name": "🔗 Repo",     "value": "[MaxLananas/MaxOS](https://github.com/MaxLananas/MaxOS)", "inline": False},
        ]
    )])

def d_analyse(score, comment, bugs, plan, manquants):
    """Rapport d'analyse détaillé."""
    # Score couleur
    if score >= 70:   score_color = 0x00FF00
    elif score >= 40: score_color = 0xFFA500
    else:             score_color = 0xFF0000

    score_bar = build_progress_bar(score)

    bugs_txt = "\n".join([
        f"🔴 `{b.get('fichier','?')}` — {b.get('description','')[:80]}"
        for b in bugs[:5]
    ]) or "✅ Aucun problème critique"

    plan_txt = "\n".join([
        f"{'🔴' if a.get('priorite')=='CRITIQUE' else '🟡' if a.get('priorite')=='HAUTE' else '🟢'} "
        f"**{a.get('nom','?')}** — {a.get('description','')[:60]}"
        for a in plan[:8]
    ]) or "Aucun"

    manq_txt = "\n".join([f"❌ `{f}`" for f in manquants[:5]]) or "✅ Tous présents"

    discord_send([make_embed(
        f"📊 Rapport d'analyse — Score {score}/100",
        f"```\n{score_bar}\n```\n_{comment}_",
        score_color,
        [
            {"name": "🐛 Problèmes détectés",  "value": bugs_txt,  "inline": False},
            {"name": "📋 Plan d'action Gemini", "value": plan_txt,  "inline": False},
            {"name": "📁 Fichiers manquants",   "value": manq_txt,  "inline": True},
            {"name": "📈 Améliorations prévues","value": str(len(plan)), "inline": True},
        ]
    )])

def d_task_start(num, total, name, priorite, desc):
    priority_emoji = {"CRITIQUE": "🔴", "HAUTE": "🟡", "NORMALE": "🟢"}.get(priorite, "⚪")
    discord_send([make_embed(
        f"⚙️ [{num}/{total}] {name}",
        f"{priority_emoji} **Priorité :** {priorite}\n\n{desc[:300]}",
        0xFFA500,
        [
            {"name": "📍 Position", "value": f"{num}/{total}", "inline": True},
            {"name": "⏱️ Démarré", "value": datetime.now().strftime("%H:%M:%S"), "inline": True},
        ]
    )])

def d_task_ok(name, files_written, elapsed, model):
    discord_send([make_embed(
        f"✅ {name}",
        "Amélioration compilée et poussée sur GitHub avec succès !",
        0x00FF00,
        [
            {"name": "📁 Fichiers modifiés", "value": "\n".join([f"`{f}`" for f in files_written]) or "?", "inline": False},
            {"name": "⏱️ Durée",   "value": f"{elapsed:.1f}s",  "inline": True},
            {"name": "🤖 Modèle",  "value": f"`{model}`",        "inline": True},
            {"name": "🔗 Commit",  "value": "[Voir sur GitHub](https://github.com/MaxLananas/MaxOS/commits/main)", "inline": False},
        ]
    )])

def d_task_err(name, reason):
    discord_send([make_embed(
        f"❌ Échec : {name}",
        f"```\n{str(reason)[:1500]}\n```",
        0xFF0000,
    )])

def d_build_err(name, log):
    """Erreur de build avec les lignes importantes."""
    error_lines = [l for l in log.split("\n") if "error:" in l.lower()][:10]
    error_txt   = "\n".join(error_lines) or log[-500:]
    discord_send([make_embed(
        f"🔨 Build échoué : {name}",
        f"Code restauré automatiquement.\n```\n{error_txt[:1500]}\n```",
        0xFF6600,
    )])

def d_final(success, total, score_before, model):
    pct   = int(success / total * 100) if total > 0 else 0
    color = 0x00FF00 if pct >= 80 else 0xFFA500 if pct >= 50 else 0xFF0000
    bar   = build_progress_bar(pct)
    discord_send([make_embed(
        f"🏁 Cycle terminé — {success}/{total} réussies",
        f"```\n{bar}\n```",
        color,
        [
            {"name": "✅ Succès",      "value": str(success),         "inline": True},
            {"name": "❌ Échecs",      "value": str(total-success),   "inline": True},
            {"name": "📊 Taux",        "value": f"{pct}%",            "inline": True},
            {"name": "🤖 Modèle",      "value": f"`{model}`",         "inline": True},
            {"name": "📈 Score avant", "value": f"{score_before}/100","inline": True},
            {"name": "🔗 GitHub",      "value": "[Voir les commits](https://github.com/MaxLananas/MaxOS/commits/main)", "inline": False},
        ]
    )])

def d_autofix(success):
    if success:
        discord_send([make_embed(
            "🔧 Auto-correction réussie !",
            "Gemini a corrigé les erreurs de compilation automatiquement.",
            0x00AAFF
        )])
    else:
        discord_send([make_embed(
            "🔧 Auto-correction échouée",
            "Impossible de corriger automatiquement. Code restauré.",
            0xFF6600
        )])

def build_progress_bar(pct, width=30):
    """Barre de progression ASCII."""
    filled = int(width * pct / 100)
    bar    = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {pct}%"

# ══════════════════════════════════════════
# GEMINI
# ══════════════════════════════════════════
def find_model():
    global WORKING_MODEL, WORKING_URL
    print("\n[Gemini] Recherche du modèle disponible...")
    for model in MODELS:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            + model
            + ":generateContent?key="
            + GEMINI_API_KEY
        )
        payload = json.dumps({
            "contents": [{"parts": [{"text": "Réponds: READY"}]}],
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
                print(f"[Gemini] ✅ {model}: {txt.strip()}")
                WORKING_MODEL = model
                WORKING_URL   = url
                return True
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"[Gemini] ❌ {model}: HTTP {e.code}")
            # Détecter clé compromise
            if e.code == 403:
                try:
                    err_data = json.loads(body)
                    err_msg  = err_data.get("error", {}).get("message", "")
                    if "leaked" in err_msg.lower() or "reported" in err_msg.lower():
                        print("=" * 60)
                        print("ALERTE SÉCURITÉ : Clé API compromise !")
                        print("Action requise :")
                        print("1. Aller sur aistudio.google.com")
                        print("2. Supprimer la clé actuelle")
                        print("3. Créer une nouvelle clé")
                        print("4. Mettre à jour le secret GitHub")
                        print("=" * 60)
                        discord_send([make_embed(
                            "🚨 ALERTE : Clé API Gemini compromise !",
                            "Google a détecté que ta clé API a été exposée.\n\n"
                            "**Actions requises :**\n"
                            "1. Aller sur [aistudio.google.com](https://aistudio.google.com)\n"
                            "2. Supprimer la clé actuelle\n"
                            "3. Créer une nouvelle clé\n"
                            "4. Mettre à jour `GEMINI_API_KEY` dans GitHub Secrets",
                            0xFF0000
                        )])
                        sys.exit(1)
                except Exception:
                    pass
            time.sleep(3)
        except Exception as e:
            print(f"[Gemini] ❌ {model}: {e}")
            time.sleep(3)
    return False

def gemini_call(prompt, max_tokens=65536, retries=3):
    global WORKING_URL, WORKING_MODEL

    if not WORKING_URL:
        if not find_model():
            return None

    # Tronquer si nécessaire (limite ~30k tokens input)
    if len(prompt) > 50000:
        print(f"[Gemini] Prompt tronqué: {len(prompt)} → 50000 chars")
        prompt = prompt[:50000] + "\n...[TRONQUÉ POUR LIMITE DE TOKENS]"

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.1,
        }
    }).encode("utf-8")

    for attempt in range(1, retries + 1):
        req = urllib.request.Request(
            WORKING_URL, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read().decode())
                # Vérifier si la réponse est complète
                finish = data["candidates"][0].get("finishReason", "STOP")
                text   = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"[Gemini] ✅ {len(text)} chars (finish: {finish})")
                return text

        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"[Gemini] HTTP {e.code} tentative {attempt}/{retries}")

            if e.code == 403:
                # Vérifier clé compromise
                try:
                    err = json.loads(body).get("error", {})
                    if "leaked" in err.get("message", "").lower():
                        print("[Gemini] FATAL: Clé compromise !")
                        discord_send([make_embed(
                            "🚨 Clé Gemini compromise !",
                            "Créer une nouvelle clé sur aistudio.google.com",
                            0xFF0000
                        )])
                        sys.exit(1)
                except Exception:
                    pass
                print(f"[Gemini] 403: {body[:300]}")
                return None

            elif e.code == 429:
                wait = 70 * attempt
                print(f"[Gemini] Rate limit → attente {wait}s")
                time.sleep(wait)

            elif e.code in (404, 400):
                print(f"[Gemini] Modèle KO → recherche alternative")
                WORKING_URL = None
                if not find_model():
                    return None
            else:
                print(f"[Gemini] Err {e.code}: {body[:200]}")
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
    """Contexte complet."""
    ctx  = "=== CODE SOURCE COMPLET DE MAXOS ===\n\n"
    ctx += "FICHIERS DU PROJET :\n"
    for f in ALL_FILES:
        s = sources.get(f)
        ctx += f"  {'[OK]' if s else '[MANQUANT]'} {f}\n"
    ctx += "\n"

    for f in ALL_FILES:
        content = sources.get(f)
        ctx += f"{'='*60}\n"
        ctx += f"FICHIER : {f}\n"
        ctx += f"{'='*60}\n"
        if content:
            ctx += content + "\n"
        else:
            ctx += "[FICHIER MANQUANT - DOIT ÊTRE CRÉÉ]\n"
        ctx += "\n"

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
        if "nothing to commit" in (out + e):
            print("[Git] Rien à committer")
            return True
        print(f"[Git] Commit KO: {e[:300]}")
        return False
    ok2, _, e2 = git(["push"])
    if not ok2:
        print(f"[Git] Push KO: {e2[:300]}")
        return False
    print(f"[Git] ✅ {msg}")
    return True

def make_build():
    subprocess.run(["make", "clean"], cwd=REPO_PATH, capture_output=True)
    r = subprocess.run(
        ["make"], cwd=REPO_PATH,
        capture_output=True, text=True,
        timeout=120
    )
    ok  = r.returncode == 0
    log = r.stdout + r.stderr
    print(f"[Build] {'✅ OK' if ok else '❌ ÉCHEC'}")
    if not ok:
        errs = [l for l in log.split("\n") if "error:" in l.lower() or "Error" in l]
        for e in errs[:5]:
            print(f"  → {e}")
    return ok, log

# ══════════════════════════════════════════
# PARSER FICHIERS
# ══════════════════════════════════════════
def parse_files(response):
    files     = {}
    cur_file  = None
    cur_lines = []
    in_file   = False

    for line in response.split("\n"):
        s = line.strip()

        # Début fichier
        if "=== FILE:" in s and s.endswith("==="):
            try:
                start = s.index("=== FILE:") + 9
                end   = s.rindex("===")
                fname = s[start:end].strip().strip("`").strip()
                cur_file  = fname
                cur_lines = []
                in_file   = True
            except Exception:
                pass
            continue

        # Fin fichier
        if s == "=== END FILE ===" and in_file:
            if cur_file:
                content = "\n".join(cur_lines).strip()
                # Nettoyer markdown
                for lang in ["```c", "```asm", "```nasm", "```makefile", "```ld", "```"]:
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
# PHASE 1 : ANALYSE AUTONOME
# ══════════════════════════════════════════
def phase_analyse(context):
    print("\n[Phase 1] Gemini analyse le code...")

    prompt = f"""Tu es un expert OS bare metal x86.
Analyse le code de MaxOS et décide toi-même ce que tu veux améliorer.

{context}

INFORMATIONS COMPILATION :
- gcc -m32 -ffreestanding -fno-stack-protector -fno-builtin -fno-pic -fno-pie -nostdlib -nostdinc -w -c
- nasm -f elf (objets) / nasm -f bin (bootloader)
- ld -m elf_i386 -T linker.ld --oformat binary
- VGA texte : 80x25, 16 couleurs, adresse 0xB8000
- Kernel chargé à : 0x8000
- Stack : 0x90000
- INTERDIT : malloc, free, printf, strcmp, strlen, memset, memcpy, stdio.h, stdlib.h, string.h

RETOURNE UNIQUEMENT LE JSON SUIVANT (pas de texte avant ou après) :
{{
  "score_actuel": 45,
  "commentaire_global": "Une phrase résumant l'état du code",
  "problemes_critiques": [
    {{"fichier": "path/fichier.c", "description": "problème précis"}}
  ],
  "fichiers_manquants": ["path/fichier.c"],
  "plan_ameliorations": [
    {{
      "nom": "Nom court",
      "priorite": "CRITIQUE",
      "fichiers_a_modifier": ["path/fichier.h", "path/fichier.c"],
      "fichiers_a_creer": [],
      "description": "Ce que tu vas faire"
    }}
  ]
}}"""

    # Appel avec moins de tokens pour l'analyse
    response = gemini_call(prompt, max_tokens=4096)
    if not response:
        return None

    print(f"[Phase 1] Réponse: {len(response)} chars")
    print(f"[Phase 1] Début: {response[:200]}")

    # Extraire JSON de manière robuste
    # Chercher { ... } même si entouré de texte
    response_clean = response.strip()

    # Cas 1 : Réponse est directement du JSON
    if response_clean.startswith("{"):
        try:
            return json.loads(response_clean)
        except Exception:
            pass

    # Cas 2 : JSON dans un bloc ```json
    if "```json" in response_clean:
        start = response_clean.index("```json") + 7
        end   = response_clean.index("```", start)
        try:
            return json.loads(response_clean[start:end].strip())
        except Exception:
            pass

    # Cas 3 : Chercher le premier { et dernier }
    i = response_clean.find("{")
    j = response_clean.rfind("}") + 1
    if i >= 0 and j > i:
        try:
            return json.loads(response_clean[i:j])
        except Exception as e:
            print(f"[Phase 1] JSON parse error: {e}")
            print(f"[Phase 1] Tentative sur: {response_clean[i:i+500]}")

    # Cas 4 : Construire un plan par défaut si Gemini ne retourne pas de JSON
    print("[Phase 1] JSON introuvable, plan par défaut...")
    return {
        "score_actuel": 40,
        "commentaire_global": "Analyse automatique - plan par défaut appliqué",
        "problemes_critiques": [],
        "fichiers_manquants": [],
        "plan_ameliorations": [
            {
                "nom": "Amélioration UI complète",
                "priorite": "HAUTE",
                "fichiers_a_modifier": ["ui/ui.h", "ui/ui.c"],
                "fichiers_a_creer": [],
                "description": "Améliorer l'interface utilisateur style Windows 11"
            },
            {
                "nom": "Terminal avec historique",
                "priorite": "HAUTE",
                "fichiers_a_modifier": ["apps/terminal.h", "apps/terminal.c"],
                "fichiers_a_creer": [],
                "description": "Ajouter historique et nouvelles commandes au terminal"
            },
            {
                "nom": "Bloc-Notes amélioré",
                "priorite": "NORMALE",
                "fichiers_a_modifier": ["apps/notepad.h", "apps/notepad.c"],
                "fichiers_a_creer": [],
                "description": "Améliorer l'éditeur de texte"
            },
            {
                "nom": "Calculatrice",
                "priorite": "NORMALE",
                "fichiers_a_modifier": ["kernel/kernel.c"],
                "fichiers_a_creer": ["apps/calculator.h", "apps/calculator.c"],
                "description": "Créer une application calculatrice"
            }
        ]
    }

# ══════════════════════════════════════════
# PHASE 2 : IMPLÉMENTATION
# ══════════════════════════════════════════
def phase_implement(amelioration, all_sources):
    nom        = amelioration.get("nom", "Amélioration")
    fichiers_m = amelioration.get("fichiers_a_modifier", [])
    fichiers_c = amelioration.get("fichiers_a_creer", [])
    desc       = amelioration.get("description", "")
    tous       = list(set(fichiers_m + fichiers_c))

    print(f"\n[Impl] {nom}")
    print(f"[Impl] Fichiers cibles: {tous}")

    # Fichiers liés automatiquement
    lies = set(tous)
    for f in tous:
        base = f.replace(".c", "").replace(".h", "")
        for ext in [".c", ".h"]:
            cand = base + ext
            if cand in all_sources:
                lies.add(cand)

    # Toujours inclure ces fichiers clés
    for key in ["kernel/kernel.c", "drivers/screen.h",
                "drivers/keyboard.h", "ui/ui.h", "Makefile"]:
        lies.add(key)

    # Contexte ciblé
    ctx = "=== FICHIERS À MODIFIER ===\n\n"
    for f in sorted(lies):
        c = all_sources.get(f, "")
        ctx += f"--- {f} ---\n"
        ctx += (c if c else "[MANQUANT - À CRÉER]\n")
        ctx += "\n\n"

    prompt = f"""Tu es un expert OS bare metal x86. Tu travailles sur MaxOS.

TÂCHE : {nom}
DESCRIPTION : {desc}

FICHIERS À MODIFIER : {fichiers_m}
FICHIERS À CRÉER    : {fichiers_c}

{ctx}

RÈGLES ABSOLUES :
1. C pur - PAS de #include librairies standard
2. PAS malloc, free, printf, strlen, strcmp, memset, memcpy
3. PAS #include <stdio.h> <stdlib.h> <string.h>
4. Compatible: gcc -m32 -ffreestanding -fno-pic -fno-pie -nostdlib -nostdinc
5. Code COMPLET dans chaque fichier (pas de "reste inchangé")
6. Si tu modifies kernel.c, donne le fichier complet avec toutes les apps
7. Si tu crées un nouveau .c, modifie le Makefile pour l'inclure

COMMENCE DIRECTEMENT PAR LES FICHIERS - PAS DE TEXTE AVANT :

=== FILE: premier/fichier.h ===
[code complet]
=== END FILE ===

=== FILE: premier/fichier.c ===
[code complet]
=== END FILE ==="""

    t0       = time.time()
    response = gemini_call(prompt, max_tokens=65536)
    elapsed  = time.time() - t0

    if not response:
        d_task_err(nom, "Gemini n'a pas répondu après 3 tentatives.")
        return False, []

    print(f"[Impl] Réponse: {len(response)} chars en {elapsed:.1f}s")

    # Parser
    files = parse_files(response)
    if not files:
        print(f"[Debug] Début réponse:\n{response[:1000]}")
        d_task_err(nom, f"Aucun fichier parsé.\n```\n{response[:800]}\n```")
        return False, []

    print(f"[Impl] Parsé: {list(files.keys())}")

    # Backup + écriture
    backs   = backup_files(list(files.keys()))
    written = write_files(files)

    if not written:
        d_task_err(nom, "Aucun fichier écrit.")
        return False, []

    # Build
    build_ok, log = make_build()

    if build_ok:
        pushed = git_push(f"feat(ai): {nom} [{WORKING_MODEL}]")
        if pushed:
            d_task_ok(nom, written, elapsed, WORKING_MODEL)
            return True, written
        d_task_err(nom, "Push Git échoué.")
        restore_files(backs)
        return False, []
    else:
        # Auto-fix
        print("[Build] Tentative auto-correction...")
        fixed = auto_fix(log, files, backs)
        if fixed:
            d_autofix(True)
            return True, written

        restore_files(backs)
        for p in written:
            if p not in backs:
                fp = os.path.join(REPO_PATH, p)
                if os.path.exists(fp):
                    os.remove(fp)

        d_build_err(nom, log)
        return False, []

# ══════════════════════════════════════════
# AUTO-FIX
# ══════════════════════════════════════════
def auto_fix(build_log, generated_files, backups):
    print("[Fix] Demande correction à Gemini...")

    current = {}
    for p in generated_files:
        fp = os.path.join(REPO_PATH, p)
        if os.path.exists(fp):
            with open(fp, "r") as f:
                current[p] = f.read()

    ctx = ""
    for p, c in current.items():
        ctx += f"--- {p} ---\n{c}\n\n"

    prompt = f"""Le code généré pour MaxOS ne compile pas.

ERREURS :
{build_log[-2000:]}


FICHIERS GÉNÉRÉS :
{ctx}

RÈGLES : C pur, gcc -m32 -ffreestanding -nostdlib -nostdinc, pas de librairies.

Corrige UNIQUEMENT les erreurs. Réponds directement avec les fichiers :

=== FILE: path/fichier.c ===
[code corrigé complet]
=== END FILE ==="""

    response = gemini_call(prompt, max_tokens=32768)
    if not response:
        return False

    files = parse_files(response)
    if not files:
        return False

    write_files(files)
    ok, log = make_build()

    if ok:
        git_push("fix(ai): Auto-correction erreurs compilation")
        return True

    d_autofix(False)
    return False

# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
def main():
    print("╔══════════════════════════════════════════════╗")
    print("║   MaxOS AI Developer v6.0                    ║")
    print("║   Sécurisé + Webhook riche + Autonome        ║")
    print("╚══════════════════════════════════════════════╝\n")

    if not find_model():
        print("FATAL: Aucun modèle disponible!")
        sys.exit(1)

    d_start(WORKING_MODEL, len(ALL_FILES))

    # Lire le code
    sources = read_all()
    context = build_context(sources)
    print(f"[Sources] {len([s for s in sources.values() if s])} fichiers OK, {len(context)} chars")

    # Phase 1 : Analyse
    print("\n" + "═"*55)
    print(" PHASE 1 : Analyse autonome")
    print("═"*55)

    analyse = phase_analyse(context)
    if not analyse:
        discord_send([make_embed(
            "❌ Analyse échouée",
            "Gemini n'a pas pu analyser le code. Vérifier la clé API.",
            0xFF0000
        )])
        sys.exit(1)

    score   = analyse.get("score_actuel", 0)
    comment = analyse.get("commentaire_global", "")
    plan    = analyse.get("plan_ameliorations", [])
    bugs    = analyse.get("problemes_critiques", [])
    manq    = analyse.get("fichiers_manquants", [])

    print(f"\n[Rapport] Score: {score}/100 — {comment}")
    print(f"[Rapport] {len(plan)} amélioration(s) planifiée(s)")
    for i, a in enumerate(plan):
        print(f"  [{i+1}] [{a.get('priorite','?')}] {a.get('nom','?')}")

    d_analyse(score, comment, bugs, plan, manq)

    # Phase 2 : Implémentation
    print("\n" + "═"*55)
    print(" PHASE 2 : Implémentation")
    print("═"*55)

    # Trier par priorité
    order   = {"CRITIQUE": 0, "HAUTE": 1, "NORMALE": 2}
    plan_ok = sorted(plan, key=lambda x: order.get(x.get("priorite","NORMALE"), 2))

    success = 0
    total   = len(plan_ok)

    for i, task in enumerate(plan_ok, 1):
        nom      = task.get("nom", f"Tâche {i}")
        priorite = task.get("priorite", "NORMALE")

        print(f"\n{'═'*55}")
        print(f" [{i}/{total}] [{priorite}] {nom}")
        print(f"{'═'*55}")

        d_task_start(i, total, nom, priorite, task.get("description",""))

        sources = read_all()
        ok, written = phase_implement(task, sources)

        if ok:
            success += 1
            sources = read_all()
            context = build_context(sources)

        if i < total:
            wait = 30
            print(f"[Pause] {wait}s...")
            time.sleep(wait)

    d_final(success, total, score, WORKING_MODEL)
    print(f"\n[FIN] {success}/{total} améliorations réussies.")

if __name__ == "__main__":
    main()
