#!/usr/bin/env python3
"""MaxOS AI Developer v4.0"""

import os, sys, json, time, subprocess
import urllib.request, urllib.error
from datetime import datetime

# ══════════════════════════════════════════
# CONFIG - Lit depuis les variables d'env
# ══════════════════════════════════════════
GEMINI_API_KEY  = os.environ.get("GEMINI_API_KEY", "")
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")
REPO_PATH       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Vérification au démarrage
print(f"[Config] Gemini key : {'OK (' + str(len(GEMINI_API_KEY)) + ' chars)' if GEMINI_API_KEY else 'MANQUANTE !'}")
print(f"[Config] Discord    : {'OK' if DISCORD_WEBHOOK else 'MANQUANT !'}")
print(f"[Config] Repo       : {REPO_PATH}")

if not GEMINI_API_KEY:
    print("ERREUR : GEMINI_API_KEY non définie !")
    print("Dans GitHub : Settings → Secrets → GEMINI_API_KEY")
    sys.exit(1)

# Modèles à tester dans l'ordre
MODELS_TO_TRY = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

WORKING_MODEL = None
WORKING_URL   = None

SOURCE_FILES = [
    "kernel/kernel.c",
    "drivers/screen.c", "drivers/screen.h",
    "drivers/keyboard.c", "drivers/keyboard.h",
    "ui/ui.c", "ui/ui.h",
    "apps/notepad.c", "apps/terminal.c",
    "apps/sysinfo.c", "apps/about.c",
    "boot/boot.asm", "Makefile", "linker.ld",
]

# ══════════════════════════════════════════
# TROUVER LE MODÈLE QUI MARCHE
# ══════════════════════════════════════════
def find_model():
    global WORKING_MODEL, WORKING_URL
    print("\n[Gemini] Test des modèles disponibles...")

    for model in MODELS_TO_TRY:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            + model
            + ":generateContent?key="
            + GEMINI_API_KEY
        )
        payload = json.dumps({
            "contents": [{"parts": [{"text": "Réponds juste OK"}]}],
            "generationConfig": {"maxOutputTokens": 5}
        }).encode()

        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read())
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"[Gemini] ✅ {model} fonctionne ! Réponse: {text.strip()}")
                WORKING_MODEL = model
                WORKING_URL   = url
                return True
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"[Gemini] ❌ {model} → HTTP {e.code}: {body[:150]}")
            time.sleep(3)
        except Exception as e:
            print(f"[Gemini] ❌ {model} → {e}")
            time.sleep(3)

    print("[Gemini] AUCUN modèle disponible !")
    return False

# ══════════════════════════════════════════
# DISCORD
# ══════════════════════════════════════════
def discord(title, msg, color=0x0099FF, fields=None):
    if not DISCORD_WEBHOOK:
        print(f"[Discord] Pas de webhook - {title}")
        return

    embed = {
        "title": str(title)[:256],
        "description": str(msg)[:2000],
        "color": color,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "footer": {"text": f"MaxOS AI v4.0 | {WORKING_MODEL or 'init'}"},
        "fields": (fields or [])[:10]
    }

    payload = json.dumps({
        "username": "MaxOS AI Bot",
        "avatar_url": "https://raw.githubusercontent.com/MaxLananas/MaxOS/main/assets/logo.png",
        "embeds": [embed]
    }).encode("utf-8")

    req = urllib.request.Request(
        DISCORD_WEBHOOK,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "DiscordBot (https://github.com/MaxLananas/MaxOS, 4.0)",
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            print(f"[Discord] ✅ Envoyé ({r.status}): {title}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"[Discord] ❌ HTTP {e.code}: {body[:300]}")
    except Exception as e:
        print(f"[Discord] ❌ {e}")

def d_ok(t, m, f=None):  discord(f"✅ {t}", m, 0x00FF00, f)
def d_err(t, m):          discord(f"❌ {t}", m, 0xFF0000)
def d_info(t, m, f=None): discord(f"ℹ️ {t}", m, 0x5865F2, f)
def d_prog(t, m):         discord(f"⚙️ {t}", m, 0xFFA500)

# ══════════════════════════════════════════
# GEMINI
# ══════════════════════════════════════════
def gemini(prompt, retries=3):
    global WORKING_URL, WORKING_MODEL

    if not WORKING_URL:
        if not find_model():
            return None

    # Tronquer si trop long
    if len(prompt) > 20000:
        prompt = prompt[:20000] + "\n...[tronqué]"

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 8192,
            "temperature": 0.15,
        }
    }).encode("utf-8")

    for attempt in range(1, retries + 1):
        req = urllib.request.Request(
            WORKING_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data  = json.loads(r.read().decode())
                text  = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"[Gemini] ✅ {len(text)} chars")
                return text

        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"[Gemini] HTTP {e.code} (tentative {attempt}/{retries})")

            if e.code == 429:
                wait = 60 * attempt
                print(f"[Gemini] Rate limit → attente {wait}s")
                time.sleep(wait)
            elif e.code in (404, 400):
                print(f"[Gemini] Modèle KO, recherche alternative...")
                WORKING_URL = None
                WORKING_MODEL = None
                if not find_model():
                    return None
                # Mettre à jour payload URL
            else:
                print(f"[Gemini] Erreur: {body[:200]}")
                time.sleep(20)

        except Exception as e:
            print(f"[Gemini] Exception: {e}")
            time.sleep(15)

    return None

# ══════════════════════════════════════════
# SOURCES
# ══════════════════════════════════════════
def read_sources():
    s = {}
    for f in SOURCE_FILES:
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                s[f] = fh.read()
    return s

def make_context(sources):
    ctx = "=== CODE MAXOS ===\n"
    for f, c in sources.items():
        ctx += f"\n[{f}]\n{c[:1500]}\n"
    return ctx

# ══════════════════════════════════════════
# GIT
# ══════════════════════════════════════════
def git_cmd(args):
    r = subprocess.run(
        ["git"] + args, cwd=REPO_PATH,
        capture_output=True, text=True
    )
    return r.returncode == 0, r.stdout, r.stderr

def push(msg):
    git_cmd(["add", "-A"])
    ok, _, e = git_cmd(["commit", "-m", msg])
    if not ok:
        if "nothing to commit" in e:
            print("[Git] Rien à committer")
            return True
        print(f"[Git] Commit KO: {e}")
        return False
    ok, _, e = git_cmd(["push"])
    if not ok:
        print(f"[Git] Push KO: {e}")
        return False
    print(f"[Git] ✅ {msg}")
    return True

def build():
    subprocess.run(["make", "clean"], cwd=REPO_PATH, capture_output=True)
    r = subprocess.run(["make"], cwd=REPO_PATH, capture_output=True, text=True)
    print(f"[Build] {'✅ OK' if r.returncode == 0 else '❌ KO'}")
    return r.returncode == 0, r.stdout + r.stderr

# ══════════════════════════════════════════
# PARSER
# ══════════════════════════════════════════
def parse(resp):
    files, cur_f, cur_l, in_f = {}, None, [], False
    for line in resp.split("\n"):
        s = line.strip()
        if s.startswith("=== FILE:") and s.endswith("==="):
            cur_f = s[9:-3].strip()
            cur_l = []
            in_f  = True
        elif s == "=== END FILE ===" and in_f:
            if cur_f:
                content = "\n".join(cur_l).strip()
                if content.startswith("```"):
                    content = "\n".join(content.split("\n")[1:])
                if content.endswith("```"):
                    content = "\n".join(content.split("\n")[:-1])
                files[cur_f] = content
            cur_f, cur_l, in_f = None, [], False
        elif in_f:
            cur_l.append(line)
    return files

def write(files):
    done = []
    for path, content in files.items():
        if path.startswith("/") or ".." in path:
            continue
        full = os.path.join(REPO_PATH, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        done.append(path)
        print(f"[Write] {path}")
    return done

def backup(paths):
    b = {}
    for p in paths:
        full = os.path.join(REPO_PATH, p)
        if os.path.exists(full):
            with open(full) as f:
                b[p] = f.read()
    return b

def restore(b):
    for p, c in b.items():
        with open(os.path.join(REPO_PATH, p), "w") as f:
            f.write(c)

# ══════════════════════════════════════════
# TÂCHES
# ══════════════════════════════════════════
TASKS = [
    {
        "name": "Analyse et score",
        "type": "analyse",
        "prompt": """Analyse ce code d'OS bare metal x86.
Retourne UNIQUEMENT ce JSON valide, rien d'autre :
{"score":75,"bugs":["exemple bug"],"ameliorations":["idée 1","idée 2"],"commentaire":"résumé"}"""
    },
    {
        "name": "UI Topbar + Taskbar style Win11",
        "type": "code",
        "prompt": """Améliore ui/ui.h et ui/ui.c pour MaxOS.
Objectif : style Windows 11, propre et moderne.
Règles : C pur, x86 32-bit bare metal, VGA 80x25, 16 couleurs, pas malloc/printf/stdlib.

Améliorations :
- Topbar avec logo stylé, onglets actifs/inactifs clairs
- Séparateurs visuels élégants
- Taskbar bas avec bouton Start bleu et apps colorées
- Indicateurs horloge/wifi/batterie

FORMAT EXACT :
=== FILE: ui/ui.h ===
[code C complet]
=== END FILE ===

=== FILE: ui/ui.c ===
[code C complet]
=== END FILE ==="""
    },
    {
        "name": "Terminal avec historique",
        "type": "code",
        "prompt": """Améliore apps/terminal.h et apps/terminal.c.
Règles : C pur, x86 32-bit bare metal, pas malloc/printf/stdlib.

Ajoute :
- Historique 15 commandes (flèche haut/bas)
- Commandes : help, clear, uname, mem, cpu, ls, date, whoami, ps, echo, ver
- Prompt coloré
- Autocomplétion basique TAB

FORMAT EXACT :
=== FILE: apps/terminal.h ===
[code C complet]
=== END FILE ===

=== FILE: apps/terminal.c ===
[code C complet]
=== END FILE ==="""
    },
    {
        "name": "Bloc-Notes amélioré",
        "type": "code",
        "prompt": """Améliore apps/notepad.h et apps/notepad.c.
Règles : C pur, x86 32-bit bare metal, pas malloc/printf/stdlib.

Améliorations :
- Curseur bloc bleu visible
- Ligne courante surlignée gris clair
- Compteur mots et caractères dans statusbar
- Home = début ligne, End = fin ligne
- Insertion de caractère (décale le reste)

FORMAT EXACT :
=== FILE: apps/notepad.h ===
[code C complet]
=== END FILE ===

=== FILE: apps/notepad.c ===
[code C complet]
=== END FILE ==="""
    },
    {
        "name": "App Calculatrice",
        "type": "code",
        "prompt": """Crée une calculatrice pour MaxOS (touche F5).
Règles : C pur, x86 32-bit bare metal, pas malloc/printf/stdlib.

Fonctions :
- Chiffres 0-9
- Opérations + - * /
- Entrée = calculer
- Echap = effacer
- Affichage grand style calculatrice Win11
- Gestion division par zéro

FORMAT EXACT :
=== FILE: apps/calculator.h ===
[code C complet]
=== END FILE ===

=== FILE: apps/calculator.c ===
[code C complet]
=== END FILE ==="""
    },
]

# ══════════════════════════════════════════
# EXÉCUTER UNE TÂCHE
# ══════════════════════════════════════════
def run(task, ctx, num, total):
    name  = task["name"]
    ttype = task["type"]

    print(f"\n{'═'*55}")
    print(f"  [{num}/{total}] {name}")
    print(f"{'═'*55}")

    d_prog(f"[{num}/{total}] {name}", "Gemini génère les améliorations...")

    prompt   = f"Code MaxOS actuel :\n{ctx}\n\n{task['prompt']}"
    t0       = time.time()
    response = gemini(prompt)
    elapsed  = time.time() - t0

    if not response:
        d_err(name, "Gemini n'a pas répondu après 3 tentatives.")
        return False

    # Analyse JSON
    if ttype == "analyse":
        try:
            i = response.find("{")
            j = response.rfind("}") + 1
            if i >= 0 and j > i:
                d = json.loads(response[i:j])
                d_info(
                    "📊 Rapport MaxOS",
                    f"Score **{d.get('score','?')}/100**\n_{d.get('commentaire','')}_",
                    [
                        {"name": "🐛 Bugs",       "value": "\n".join(d.get("bugs",[])[:3]) or "Aucun", "inline": True},
                        {"name": "💡 Améliorations", "value": "\n".join(d.get("ameliorations",[])[:3]), "inline": True},
                    ]
                )
            else:
                d_info("Analyse", response[:800])
        except Exception as ex:
            print(f"[JSON] {ex}")
            d_info("Analyse brute", response[:600])
        return True

    # Code → parser → écrire → build → push
    files = parse(response)
    if not files:
        d_err(name, f"Aucun fichier trouvé dans la réponse.\nDébut:\n```\n{response[:500]}\n```")
        return False

    print(f"[Parser] {len(files)} fichier(s): {list(files.keys())}")

    backs   = backup(list(files.keys()))
    written = write(files)

    if not written:
        d_err(name, "Aucun fichier écrit (chemins invalides ?).")
        return False

    build_ok, log = build()

    if build_ok:
        pushed = push(f"feat(ai): {name} [{WORKING_MODEL}]")
        if pushed:
            d_ok(
                name,
                f"Code amélioré, compilé et poussé sur GitHub !",
                [
                    {"name": "📁 Fichiers", "value": "\n".join(written),     "inline": False},
                    {"name": "⏱️ Durée",   "value": f"{elapsed:.1f}s",       "inline": True},
                    {"name": "🤖 Modèle",  "value": WORKING_MODEL or "?",    "inline": True},
                ]
            )
            return True
        d_err(name, "Push Git échoué.")
        return False
    else:
        restore(backs)
        for p in written:
            if p not in backs:
                fp = os.path.join(REPO_PATH, p)
                if os.path.exists(fp):
                    os.remove(fp)
        d_err(name, f"Compilation échouée, code restauré.\n```\n{log[-600:]}\n```")
        return False

# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════
def main():
    print("╔══════════════════════════════════════════╗")
    print("║   MaxOS AI Developer v4.0                ║")
    print("║   Variables d'environnement + Multi-model║")
    print("╚══════════════════════════════════════════╝\n")

    # Trouver le bon modèle
    if not find_model():
        print("FATAL: Aucun modèle Gemini disponible.")
        d_err("Démarrage échoué", "Aucun modèle Gemini accessible avec cette clé API.")
        sys.exit(1)

    d_info(
        "MaxOS AI v4.0 démarré ! 🚀",
        f"Modèle : **{WORKING_MODEL}**\n{len(TASKS)} tâches planifiées",
        [{"name": "⏰ Heure", "value": datetime.now().strftime("%H:%M:%S"), "inline": True}]
    )

    sources = read_sources()
    ctx     = make_context(sources)
    print(f"[Sources] {len(sources)} fichiers, {len(ctx)} chars de contexte")

    success = 0
    for i, task in enumerate(TASKS, 1):
        try:
            if run(task, ctx, i, len(TASKS)):
                success += 1
                sources = read_sources()
                ctx     = make_context(sources)

            if i < len(TASKS):
                print(f"[Pause] 25s avant la prochaine tâche...")
                time.sleep(25)

        except KeyboardInterrupt:
            d_info("Arrêt manuel", f"{success} tâches complétées.")
            sys.exit(0)
        except Exception as ex:
            print(f"[ERREUR] {ex}")
            d_err(f"Erreur tâche {i}", str(ex)[:500])

    color = 0x00FF00 if success == len(TASKS) else 0xFFA500
    discord(
        f"🏁 Cycle terminé : {success}/{len(TASKS)}",
        f"**{success} améliorations** appliquées à MaxOS !",
        color,
        [
            {"name": "✅ Succès", "value": str(success),              "inline": True},
            {"name": "❌ Échecs", "value": str(len(TASKS) - success), "inline": True},
            {"name": "🤖 Modèle", "value": WORKING_MODEL or "?",      "inline": True},
        ]
    )
    print(f"\n[FIN] {success}/{len(TASKS)} tâches réussies.")

if __name__ == "__main__":
    main()
