# MaxOS AI v8.0 - Plan Complet

Félicitations, le système fonctionne ! Maintenant on va tout passer au niveau supérieur.

---

## 1. LES CLÉS GEMINI - Format des Secrets

### Format actuel (1 clé)
Va dans **Settings → Secrets and variables → Actions → New repository secret** :

```
Nom   : GEMINI_API_KEY
Valeur: AIzaSy...ta_cle_ici
```

### Système multi-clés (ajouter quand tu veux)
Le nouveau système lit automatiquement ces secrets :
```
GEMINI_API_KEY    ← ta clé actuelle (obligatoire)
GEMINI_API_KEY_2  ← 2ème clé (optionnelle)
GEMINI_API_KEY_3  ← 3ème clé (optionnelle)
```
**Tu ajoutes juste le secret, le code détecte tout seul.**

---

## 2. EST-CE QUE ÇA TOURNE 24/7 ?

**Presque.** Le cron actuel : `'0 */6 * * *'` = toutes les 6h.

On va passer à **toutes les 2h** et ajouter un **auto-relance** si le job échoue.

---

## 3. TESTER L'OS EN LOCAL

### Windows
```powershell
# Installer QEMU : https://www.qemu.org/windows/
# Télécharger build/os.img depuis les artifacts GitHub Actions
# Puis :
qemu-system-i386 -drive format=raw,file=os.img,if=floppy -boot a -vga std -k fr
```

### Ubuntu/Debian
```bash
sudo apt install qemu-system-x86
# Télécharger os.img
qemu-system-i386 -drive format=raw,file=os.img,if=floppy -boot a -vga std -k fr
```

### Compiler toi-même
```bash
sudo apt install nasm gcc make qemu-system-x86
git clone https://github.com/MaxLananas/MaxOS
cd MaxOS
make
qemu-system-i386 -drive format=raw,file=os.img,if=floppy -boot a -vga std -k fr
```

---

## 4. LES NOUVEAUX FICHIERS À REMPLACER

### `ai_dev/maxos_ai.py` - Version 8.0 complète

```python
#!/usr/bin/env python3
"""MaxOS AI Developer v8.0 - Multi-Key + Parallel + Windows-11-scale ambition"""

import os, sys, json, time, subprocess, hashlib, random
import urllib.request, urllib.error
from datetime import datetime

# ══════════════════════════════════════════════════════════════════
# CONFIGURATION MULTI-CLÉS
# ══════════════════════════════════════════════════════════════════
def load_api_keys():
    """Charge toutes les clés Gemini disponibles automatiquement."""
    keys = []
    # Clé principale
    k1 = os.environ.get("GEMINI_API_KEY", "")
    if k1:
        keys.append(k1)
    # Clés supplémentaires (GEMINI_API_KEY_2, _3, _4, _5...)
    for i in range(2, 10):
        k = os.environ.get(f"GEMINI_API_KEY_{i}", "")
        if k:
            keys.append(k)
    return keys

API_KEYS        = load_api_keys()
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")
GITHUB_TOKEN    = os.environ.get("GITHUB_TOKEN", "")
REPO_OWNER      = os.environ.get("REPO_OWNER", "MaxLananas")
REPO_NAME       = os.environ.get("REPO_NAME", "MaxOS")
REPO_PATH       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# État de rotation des clés
KEY_STATE = {
    "current_index": 0,
    "cooldowns": {},       # key_index -> timestamp de fin de cooldown
    "usage_count": {},     # key_index -> nombre d'appels
    "errors": {},          # key_index -> nombre d'erreurs
}

def mask_key(k):
    if len(k) > 8:
        return k[:4] + "*" * max(0, len(k)-8) + k[-4:]
    return "***"

print(f"[Config] Clés Gemini : {len(API_KEYS)} clé(s) chargée(s)")
for i, k in enumerate(API_KEYS):
    print(f"         Clé {i+1}      : {mask_key(k)}")
print(f"[Config] Discord     : {'OK' if DISCORD_WEBHOOK else 'ABSENT'}")
print(f"[Config] GitHub      : {'OK' if GITHUB_TOKEN else 'ABSENT'}")
print(f"[Config] Repo        : {REPO_OWNER}/{REPO_NAME}")
print(f"[Config] Path        : {REPO_PATH}")

if not API_KEYS:
    print("FATAL: Aucune GEMINI_API_KEY trouvée")
    sys.exit(1)

# ══════════════════════════════════════════════════════════════════
# MODÈLES GEMINI PAR PRIORITÉ
# ══════════════════════════════════════════════════════════════════
MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

# Modèles actifs par clé : key_index -> {"model": str, "url": str}
ACTIVE_MODELS = {}

# ══════════════════════════════════════════════════════════════════
# TOUS LES FICHIERS DU PROJET
# ══════════════════════════════════════════════════════════════════
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

# ══════════════════════════════════════════════════════════════════
# MISSION PRINCIPALE - OBJECTIF WINDOWS 11
# ══════════════════════════════════════════════════════════════════
OS_MISSION = """
╔══════════════════════════════════════════════════════════════╗
║           MISSION MAXOS - OBJECTIF WINDOWS 11               ║
╚══════════════════════════════════════════════════════════════╝

MaxOS a pour ambition de devenir un OS complet à l'échelle de Windows 11.
L'IA est le développeur principal, autonome, 24h/24 7j/7.

FONCTIONNALITÉS À IMPLÉMENTER (par ordre de priorité) :
═══════════════════════════════════════════════════════

COUCHE 1 - FONDATIONS (bare metal) :
  ✦ Gestionnaire de mémoire (paging, allocation zones)
  ✦ GDT/IDT robustes avec tous les handlers d'exceptions
  ✦ Timer PIT (Programmable Interval Timer)
  ✦ Interruptions hardware complètes (IRQ 0-15)
  ✦ Mode protégé 32-bit stable
  ✦ Pile d'appels système (syscall interface)

COUCHE 2 - DRIVERS :
  ✦ Driver clavier PS/2 complet (toutes touches, modificateurs)
  ✦ Driver VGA texte 80x25 avec couleurs 16
  ✦ Driver VGA graphique VESA (résolution 320x200 puis 640x480)
  ✦ Driver disquette/disque (lecture secteurs)
  ✦ Driver série COM1 (debug output)
  ✦ Driver son PC speaker (beeps, mélodies)
  ✦ Driver timer hardware

COUCHE 3 - SYSTÈME DE FICHIERS :
  ✦ FAT12 sur disquette (lecture/écriture)
  ✦ VFS (Virtual File System) abstrait
  ✦ Répertoires, fichiers, permissions basiques

COUCHE 4 - INTERFACE GRAPHIQUE :
  ✦ Fenêtres avec barres de titre, bordures, boutons
  ✦ Système de fenêtres empilées (z-order)
  ✦ Curseur souris PS/2 (driver + rendu)
  ✦ Desktop avec fond d'écran
  ✦ Taskbar style Windows 11
  ✦ Menu démarrer
  ✦ Icônes d'applications
  ✦ Animations (curseur clignotant, transitions)

COUCHE 5 - APPLICATIONS :
  ✦ Explorateur de fichiers
  ✦ Éditeur de texte avancé (bloc-notes)
  ✦ Terminal / Invite de commandes
  ✦ Gestionnaire des tâches
  ✦ Calculatrice
  ✦ Visualiseur d'images (formats simples)
  ✦ Horloge / Calendrier
  ✦ Jeux simples (Snake, Tetris, Pong)
  ✦ Navigateur de configuration système
  ✦ Éditeur hexadécimal
  ✦ Lecteur de musique (PC speaker)

COUCHE 6 - RÉSEAU (avancé) :
  ✦ Driver NE2000 (carte réseau émulée QEMU)
  ✦ Stack TCP/IP minimale
  ✦ DHCP client
  ✦ Ping

RÈGLES ABSOLUES DE DÉVELOPPEMENT :
═══════════════════════════════════
• Chaque amélioration doit compiler et booter dans QEMU
• Code C pure bare metal : ZÉRO librairie standard
• Pas de malloc - gestionnaire mémoire custom
• Chaque commit améliore visiblement l'OS
• L'IA peut créer, supprimer et modifier n'importe quel fichier
• Préférer la stabilité à la complexité (si ça crash, c'est nul)
• Documenter chaque nouvelle fonctionnalité dans le code
"""

# ══════════════════════════════════════════════════════════════════
# RÈGLES BARE METAL ABSOLUES
# ══════════════════════════════════════════════════════════════════
BARE_METAL_RULES = """
RÈGLES ABSOLUES BARE METAL x86 (VIOLATION = ÉCHEC DE COMPILATION) :

1. ZÉRO include de librairie standard :
   PAS #include <stddef.h>, <string.h>, <stdlib.h>, <stdio.h>,
       <stdint.h>, <stdbool.h>

2. ZÉRO types de librairie :
   PAS size_t → unsigned int
   PAS NULL   → 0
   PAS bool   → int
   PAS true/false → 1/0
   PAS uint32_t → unsigned int
   PAS int32_t  → int

3. ZÉRO fonctions de librairie :
   PAS malloc/free, memset/memcpy, strlen/strcmp, printf/sprintf

4. FONCTIONS EXISTANTES À RESPECTER :
   - nb_init(), nb_draw(), nb_key(char k) → notepad
   - tm_init(), tm_draw(), tm_key(char k) → terminal
   - si_draw() → sysinfo (PAS si_init, PAS si_key)
   - ab_draw() → about   (PAS ab_init, PAS ab_key)
   - kb_init(), kb_haskey(), kb_getchar() → keyboard
   - v_init(), v_put(), v_str(), v_fill() → screen

5. ASSEMBLY NASM uniquement dans les .asm

6. COMPILATION :
   gcc -m32 -ffreestanding -fno-stack-protector -fno-builtin
       -fno-pic -fno-pie -nostdlib -nostdinc -w -c
   nasm -f elf (pour .o) / nasm -f bin (pour boot.bin)
   ld -m elf_i386 -T linker.ld --oformat binary

7. L'IA PEUT :
   - Créer de nouveaux fichiers .c/.h/.asm
   - Supprimer des fichiers obsolètes
   - Modifier le Makefile pour intégrer les nouveaux fichiers
   - Restructurer le projet si nécessaire
   - Tout cela dans le respect des règles bare metal
"""

# ══════════════════════════════════════════════════════════════════
# ROTATION DES CLÉS INTELLIGENTE
# ══════════════════════════════════════════════════════════════════
def get_best_key():
    """Retourne l'index de la meilleure clé disponible."""
    now = time.time()
    n = len(API_KEYS)

    # Chercher une clé sans cooldown
    for attempt in range(n):
        idx = (KEY_STATE["current_index"] + attempt) % n
        cooldown_end = KEY_STATE["cooldowns"].get(idx, 0)
        if now >= cooldown_end:
            KEY_STATE["current_index"] = idx
            KEY_STATE["usage_count"][idx] = KEY_STATE["usage_count"].get(idx, 0) + 1
            return idx

    # Toutes les clés en cooldown → attendre la moins longue
    min_idx = min(KEY_STATE["cooldowns"].keys(), key=lambda i: KEY_STATE["cooldowns"][i])
    wait = KEY_STATE["cooldowns"][min_idx] - now + 1
    print(f"[Keys] Toutes les clés en cooldown. Attente {wait:.0f}s (clé {min_idx+1})")
    time.sleep(wait)
    return min_idx

def set_key_cooldown(key_idx, seconds):
    """Met une clé en cooldown."""
    KEY_STATE["cooldowns"][key_idx] = time.time() + seconds
    KEY_STATE["errors"][key_idx] = KEY_STATE["errors"].get(key_idx, 0) + 1
    n = len(API_KEYS)
    if n > 1:
        next_idx = (key_idx + 1) % n
        KEY_STATE["current_index"] = next_idx
        print(f"[Keys] Clé {key_idx+1} en cooldown {seconds}s → bascule sur clé {next_idx+1}")
    else:
        print(f"[Keys] Clé unique en cooldown {seconds}s")

def key_status_str():
    """Retourne un résumé de l'état des clés."""
    now = time.time()
    lines = []
    for i, k in enumerate(API_KEYS):
        cd = KEY_STATE["cooldowns"].get(i, 0)
        usage = KEY_STATE["usage_count"].get(i, 0)
        errors = KEY_STATE["errors"].get(i, 0)
        status = "✓ OK" if now >= cd else f"⏳ CD {int(cd-now)}s"
        model = ACTIVE_MODELS.get(i, {}).get("model", "?")
        lines.append(f"Clé {i+1}: {status} | {usage} req | {errors} err | {model}")
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════
# GITHUB API
# ══════════════════════════════════════════════════════════════════
def github_api(method, endpoint, data=None):
    if not GITHUB_TOKEN:
        return None
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/{endpoint}"
    payload = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        url, data=payload,
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
        print(f"[GitHub] {method} {endpoint} → HTTP {e.code}: {body[:200]}")
        return None
    except Exception as e:
        print(f"[GitHub] Erreur: {e}")
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
        print(f"[GitHub] Release créée: {result['html_url']}")
        return result["html_url"]
    return None

def github_create_issue(title, body, labels=None):
    data = {"title": title, "body": body, "labels": labels or []}
    result = github_api("POST", "issues", data)
    if result and "html_url" in result:
        return result["html_url"]
    return None

def github_close_issue(issue_number):
    github_api("PATCH", f"issues/{issue_number}", {"state": "closed"})

def github_get_open_issues():
    result = github_api("GET", "issues?state=open&labels=ai-task&per_page=10")
    return result if isinstance(result, list) else []

def github_get_stats():
    """Récupère les stats du repo."""
    repo = github_api("GET", "")
    commits = github_api("GET", "commits?per_page=5")
    return repo, commits

def github_create_milestone(title, description):
    data = {"title": title, "description": description, "state": "open"}
    result = github_api("POST", "milestones", data)
    if result:
        return result.get("number")
    return None

# ══════════════════════════════════════════════════════════════════
# DISCORD
# ══════════════════════════════════════════════════════════════════
def discord_send(embeds):
    if not DISCORD_WEBHOOK:
        return
    payload = json.dumps({
        "username": "MaxOS AI Bot 🤖",
        "avatar_url": "https://raw.githubusercontent.com/MaxLananas/MaxOS/main/README.md",
        "embeds": embeds[:10]
    }).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WEBHOOK, data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "DiscordBot"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return True
    except Exception as e:
        print(f"[Discord] Err: {e}")
    return False

def make_embed(title, desc, color, fields=None):
    active_keys = sum(1 for i in range(len(API_KEYS))
                     if time.time() >= KEY_STATE["cooldowns"].get(i, 0))
    current_model = ACTIVE_MODELS.get(KEY_STATE["current_index"], {}).get("model", "init")
    e = {
        "title": str(title)[:256],
        "description": str(desc)[:4096],
        "color": color,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "footer": {
            "text": (f"MaxOS AI v8.0  |  {current_model}  |  "
                    f"{active_keys}/{len(API_KEYS)} clés  |  {REPO_OWNER}/{REPO_NAME}"),
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

# ══════════════════════════════════════════════════════════════════
# GEMINI - AVEC ROTATION AUTOMATIQUE
# ══════════════════════════════════════════════════════════════════
def find_model_for_key(key_idx):
    """Trouve le meilleur modèle pour une clé donnée."""
    key = API_KEYS[key_idx]
    for model in MODELS:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            + model + ":generateContent?key=" + key
        )
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
                print(f"[Gemini] Clé {key_idx+1} → {model} OK ({txt.strip()})")
                ACTIVE_MODELS[key_idx] = {"model": model, "url": url}
                return True
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"[Gemini] Clé {key_idx+1} {model}: HTTP {e.code}")
            if e.code == 403:
                try:
                    msg = json.loads(body).get("error", {}).get("message", "")
                    if "leaked" in msg.lower():
                        print(f"FATAL: Clé {key_idx+1} compromise!")
                        d(f"🚨 ALERTE SÉCURITÉ - Clé {key_idx+1}",
                          "Clé Gemini compromise. Révoquer immédiatement.", 0xFF0000)
                        API_KEYS[key_idx] = ""
                        return False
                except Exception:
                    pass
            time.sleep(1)
        except Exception as e:
            print(f"[Gemini] Clé {key_idx+1} {model}: {e}")
            time.sleep(1)
    return False

def find_all_models():
    """Initialise tous les modèles pour toutes les clés disponibles."""
    print(f"\n[Gemini] Initialisation de {len(API_KEYS)} clé(s)...")
    success = 0
    for i in range(len(API_KEYS)):
        if API_KEYS[i]:
            if find_model_for_key(i):
                success += 1
    print(f"[Gemini] {success}/{len(API_KEYS)} clé(s) opérationnelles")
    return success > 0

def gemini(prompt, max_tokens=65536, retries=3, preferred_key=None):
    """Appel Gemini avec rotation automatique des clés."""
    if not ACTIVE_MODELS:
        if not find_all_models():
            return None

    if len(prompt) > 60000:
        prompt = prompt[:60000] + "\n...[TRONQUÉ]"

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.05,
        }
    }).encode("utf-8")

    total_attempts = retries * len(API_KEYS)

    for attempt in range(1, total_attempts + 1):
        key_idx = get_best_key() if preferred_key is None else preferred_key

        if key_idx not in ACTIVE_MODELS:
            if not find_model_for_key(key_idx):
                continue

        model_info = ACTIVE_MODELS[key_idx]
        url = model_info["url"].split("?")[0] + "?key=" + API_KEYS[key_idx]

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
                print(f"[Gemini] Clé {key_idx+1} → {len(text)} chars (finish={finish})")
                return text

        except urllib.error.HTTPError as e:
            body = e.read().decode()
            print(f"[Gemini] Clé {key_idx+1} HTTP {e.code} tentative {attempt}/{total_attempts}")

            if e.code == 429:
                # Rate limit → cooldown et rotation
                wait = min(60 * (1 + KEY_STATE["errors"].get(key_idx, 0)), 300)
                set_key_cooldown(key_idx, wait)
                # Essayer une autre clé immédiatement si disponible
                if len(API_KEYS) > 1:
                    print(f"[Gemini] Rotation vers autre clé...")
                    continue
                time.sleep(min(wait, 60))

            elif e.code in (404, 400):
                # Modèle pas disponible → chercher un autre modèle
                del ACTIVE_MODELS[key_idx]
                find_model_for_key(key_idx)

            elif e.code == 403:
                try:
                    msg = json.loads(body).get("error", {}).get("message", "")
                    if "leaked" in msg.lower():
                        d("🚨 ALERTE", f"Clé {key_idx+1} compromise!", 0xFF0000)
                        sys.exit(1)
                except Exception:
                    pass
                set_key_cooldown(key_idx, 600)

            else:
                time.sleep(20)

        except Exception as e:
            print(f"[Gemini] Clé {key_idx+1} Exception: {e}")
            time.sleep(15)

    return None

def gemini_fast(prompt, max_tokens=2000):
    """Appel rapide avec le modèle lite."""
    return gemini(prompt, max_tokens=max_tokens)

# ══════════════════════════════════════════════════════════════════
# SOURCES
# ══════════════════════════════════════════════════════════════════
def discover_files():
    """Découvre tous les fichiers du projet dynamiquement."""
    found = []
    extensions = {".c", ".h", ".asm", ".ld", "Makefile", ".py"}
    exclude_dirs = {".git", "build", "__pycache__", ".github"}
    exclude_files = {"screen.h.save"}

    for root, dirs, files in os.walk(REPO_PATH):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for f in files:
            if f in exclude_files:
                continue
            ext = os.path.splitext(f)[1]
            if ext in extensions or f == "Makefile":
                rel = os.path.relpath(os.path.join(root, f), REPO_PATH)
                rel = rel.replace("\\", "/")
                found.append(rel)

    return sorted(found)

def read_all():
    """Lit tous les fichiers du projet."""
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
    """Construit le contexte source avec limite de taille."""
    ctx = "=== CODE SOURCE COMPLET DE MAXOS ===\n\n"

    # Index des fichiers
    ctx += "FICHIERS:\n"
    for f, c in sources.items():
        ctx += f"  {'[OK]' if c else '[MANQUANT]'} {f}\n"
    ctx += "\n"

    # Contenu avec limite
    chars_used = len(ctx)
    for f, c in sources.items():
        if c is None:
            continue
        block = f"{'='*60}\nFICHIER: {f}\n{'='*60}\n{c}\n\n"
        if chars_used + len(block) > max_chars:
            ctx += f"[... {f} tronqué pour limite de taille ...]\n"
            continue
        ctx += block
        chars_used += len(block)

    return ctx

def get_project_stats(sources):
    """Calcule les stats du projet."""
    total_lines = 0
    total_files = 0
    languages = {}
    for f, c in sources.items():
        if c:
            total_files += 1
            lines = c.count("\n")
            total_lines += lines
            ext = os.path.splitext(f)[1] or f
            languages[ext] = languages.get(ext, 0) + lines
    return {
        "files": total_files,
        "lines": total_lines,
        "languages": languages,
    }

# ══════════════════════════════════════════════════════════════════
# GIT & BUILD
# ══════════════════════════════════════════════════════════════════
def git(args):
    r = subprocess.run(
        ["git"] + args, cwd=REPO_PATH,
        capture_output=True, text=True
    )
    return r.returncode == 0, r.stdout, r.stderr

def generate_commit_message(task_name, files_written, description, model_used):
    """Génère un message de commit technique et précis."""
    now = datetime.utcnow()

    # Catégorie basée sur les fichiers
    if any("kernel" in f for f in files_written):
        category = "kernel"
    elif any("driver" in f or "drivers" in f for f in files_written):
        category = "driver"
    elif any("boot" in f for f in files_written):
        category = "boot"
    elif any("ui" in f for f in files_written):
        category = "ui"
    elif any("app" in f for f in files_written):
        category = "feat(apps)"
    else:
        category = "feat"

    # Résumé des fichiers
    files_summary = ", ".join([os.path.basename(f) for f in files_written[:4]])
    if len(files_written) > 4:
        files_summary += f" +{len(files_written)-4}"

    # Corps du message
    body_lines = [
        f"",
        f"Component : {', '.join(set(f.split('/')[0] for f in files_written if '/' in f))}",
        f"Files     : {', '.join(files_written)}",
        f"Model     : {model_used}",
        f"Timestamp : {now.strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"",
        f"Changes:",
        f"  - {description}",
        f"",
        f"Technical details:",
        f"  Architecture: x86 32-bit Protected Mode",
        f"  Compiler flags: -m32 -ffreestanding -nostdlib -nostdinc",
        f"  Assembler: NASM ELF32",
    ]

    short = f"{category}: {task_name} [{files_summary}]"
    full = short + "\n" + "\n".join(body_lines)
    return short, full

def git_push(task_name, files_written, description, model_used):
    """Commit et push avec message technique détaillé."""
    short_msg, full_msg = generate_commit_message(
        task_name, files_written, description, model_used
    )

    git(["add", "-A"])
    ok, out, e = git(["commit", "-m", full_msg])
    if not ok:
        if "nothing to commit" in (out + e):
            print("[Git] Rien à committer")
            return True, None, None
        print(f"[Git] Commit KO: {e[:200]}")
        return False, None, None

    _, sha, _ = git(["rev-parse", "HEAD"])
    sha = sha.strip()[:7]

    ok2, _, e2 = git(["push"])
    if not ok2:
        print(f"[Git] Push KO: {e2[:200]}")
        return False, None, None

    print(f"[Git] ✓ Commit {sha}: {short_msg}")
    return True, sha, short_msg

def make_build():
    """Compile le projet et retourne (success, log, errors)."""
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
        line_l = line.lower()
        if "error:" in line_l:
            errors.append(line.strip())
        elif "warning:" in line_l:
            warnings.append(line.strip())

    print(f"[Build] {'✓ OK' if ok else '✗ ÉCHEC'} "
          f"({len(errors)} erreurs, {len(warnings)} warnings)")
    if not ok:
        for e in errors[:8]:
            print(f"  ✗ {e}")

    return ok, log, errors[:15]

# ══════════════════════════════════════════════════════════════════
# PARSER DE FICHIERS
# ══════════════════════════════════════════════════════════════════
def parse_files(response):
    """Parse la réponse de l'IA pour extraire les fichiers."""
    files = {}
    cur_file = None
    cur_lines = []
    in_file = False

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
                for lang in ["```c", "```asm", "```nasm", "```makefile",
                             "```ld", "```bash", "```"]:
                    if content.startswith(lang):
                        content = content[len(lang):].lstrip("\n")
                        break
                if content.endswith("```"):
                    content = content[:-3].rstrip("\n")
                files[cur_file] = content
                print(f"[Parse] ✓ {cur_file} ({len(content)} chars)")
            cur_file = None
            cur_lines = []
            in_file = False
            continue

        if in_file:
            cur_lines.append(line)

    # Détecter aussi les fichiers à supprimer
    to_delete = []
    for line in response.split("\n"):
        s = line.strip()
        if "=== DELETE:" in s and s.endswith("==="):
            try:
                start = s.index("=== DELETE:") + 11
                end = s.rindex("===")
                fname = s[start:end].strip()
                to_delete.append(fname)
                print(f"[Parse] 🗑 Suppression demandée: {fname}")
            except Exception:
                pass

    return files, to_delete

def write_files(files):
    """Écrit les fichiers générés."""
    written = []
    for path, content in files.items():
        if path.startswith("/") or ".." in path:
            print(f"[Write] ⚠ Chemin suspect ignoré: {path}")
            continue
        full = os.path.join(REPO_PATH, path)
        os.makedirs(os.path.dirname(full) if os.path.dirname(full) else REPO_PATH, exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        written.append(path)
        print(f"[Write] ✓ {path} ({len(content)} chars)")
    return written

def delete_files(paths):
    """Supprime les fichiers demandés."""
    deleted = []
    for path in paths:
        if path.startswith("/") or ".." in path:
            continue
        full = os.path.join(REPO_PATH, path)
        if os.path.exists(full):
            os.remove(full)
            deleted.append(path)
            print(f"[Delete] 🗑 {path}")
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
        os.makedirs(os.path.dirname(full) if os.path.dirname(full) else REPO_PATH, exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(c)
    print(f"[Restore] ↩ {len(backups)} fichier(s) restauré(s)")

# ══════════════════════════════════════════════════════════════════
# PHASE 1 : ANALYSE AVANCÉE
# ══════════════════════════════════════════════════════════════════
def phase_analyse(context, stats):
    print("\n[Phase 1] Analyse en cours...")

    prompt = f"""Tu es un expert OS bare metal x86.

{BARE_METAL_RULES}

{OS_MISSION}

{context}

STATISTIQUES ACTUELLES DU PROJET :
- Fichiers : {stats['files']}
- Lignes de code : {stats['lines']}

Analyse le code de MaxOS et retourne UNIQUEMENT ce JSON valide.
PAS de texte avant ou après, PAS de ```json.
Commence directement par {{ :

{{
  "score_actuel": 45,
  "niveau_os": "Bootloader basique",
  "commentaire_global": "Phrase courte",
  "fonctionnalites_presentes": ["Boot x86", "Mode texte VGA"],
  "fonctionnalites_manquantes_critiques": ["Gestionnaire mémoire", "IDT complète"],
  "problemes_critiques": [
    {{"fichier": "kernel/kernel.c", "description": "problème précis", "impact": "CRITIQUE"}}
  ],
  "fichiers_obsoletes": [],
  "plan_ameliorations": [
    {{
      "nom": "Nom technique précis",
      "priorite": "CRITIQUE",
      "categorie": "kernel|driver|ui|app|fs|network",
      "fichiers_a_modifier": ["ui/ui.c"],
      "fichiers_a_creer": [],
      "fichiers_a_supprimer": [],
      "description": "Description technique précise avec objectifs mesurables",
      "impact_attendu": "Ce que l'utilisateur verra/ressentira",
      "complexite": "FAIBLE|MOYENNE|HAUTE"
    }}
  ],
  "prochaine_milestone": "Nom de la prochaine étape majeure"
}}"""

    response = gemini(prompt, max_tokens=4000)
    if not response:
        return None

    print(f"[Phase 1] {len(response)} chars reçus")

    clean = response.strip()
    if clean.startswith("```"):
        lines = clean.split("\n")[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        clean = "\n".join(lines).strip()

    # Nettoyer les backslashes problématiques dans les strings JSON
    import re
    clean = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', clean)

    for attempt in range(3):
        i = clean.find("{")
        j = clean.rfind("}") + 1
        if i >= 0 and j > i:
            try:
                return json.loads(clean[i:j])
            except json.JSONDecodeError as e:
                print(f"[Phase 1] JSON erreur tentative {attempt+1}: {e}")
                if attempt == 0:
                    # Tentative de nettoyage agressif
                    clean = re.sub(r'(?<!\\)"(?![:,\}\]]|[^"]*":)', '\\"', clean[i:j])

    # Plan par défaut ambitieux
    print("[Phase 1] Plan par défaut")
    return {
        "score_actuel": 30,
        "niveau_os": "Prototype bare metal",
        "commentaire_global": "OS fonctionnel basique, nombreuses améliorations possibles",
        "fonctionnalites_presentes": ["Boot x86", "Mode texte VGA", "Keyboard PS/2", "Apps basiques"],
        "fonctionnalites_manquantes_critiques": [
            "Gestionnaire de mémoire", "IDT complète", "Timer PIT",
            "Mode graphique VESA", "Système de fichiers FAT12"
        ],
        "problemes_critiques": [],
        "fichiers_obsoletes": [],
        "plan_ameliorations": [
            {
                "nom": "Implémentation IDT + Gestionnaire d'exceptions x86",
                "priorite": "CRITIQUE",
                "categorie": "kernel",
                "fichiers_a_modifier": ["kernel/kernel.c", "kernel/kernel_entry.asm"],
                "fichiers_a_creer": ["kernel/idt.h", "kernel/idt.c"],
                "fichiers_a_supprimer": [],
                "description": "Implémenter la IDT complète (256 entrées), handlers pour exceptions 0-31 (division par zéro, page fault, etc.), et IRQ hardware 0-15. Utiliser NASM pour les stubs d'interruption.",
                "impact_attendu": "OS stable, pas de triple fault, exceptions catchées proprement",
                "complexite": "HAUTE"
            },
            {
                "nom": "Timer PIT 8253 + scheduler tick",
                "priorite": "CRITIQUE",
                "categorie": "kernel",
                "fichiers_a_modifier": ["kernel/kernel.c"],
                "fichiers_a_creer": ["kernel/timer.h", "kernel/timer.c"],
                "fichiers_a_supprimer": [],
                "description": "Configurer le PIT 8253 à 100Hz. Implémenter un compteur de ticks et une fonction sleep(). Base pour le multitasking futur.",
                "impact_attendu": "Animations fluides, horloge système, base pour scheduler",
                "complexite": "MOYENNE"
            },
            {
                "nom": "Gestionnaire de mémoire physique - bitmap allocator",
                "priorite": "HAUTE",
                "categorie": "kernel",
                "fichiers_a_modifier": ["kernel/kernel.c"],
                "fichiers_a_creer": ["kernel/memory.h", "kernel/memory.c"],
                "fichiers_a_supprimer": [],
                "description": "Implémenter un allocateur mémoire basique par bitmap (4KB pages). Fonctions: mem_init(), mem_alloc_page(), mem_free_page(). Zone mémoire 1MB-16MB.",
                "impact_attendu": "Allocation dynamique de mémoire, base pour applications complexes",
                "complexite": "HAUTE"
            },
            {
                "nom": "Interface graphique VESA 320x200 mode 13h",
                "priorite": "HAUTE",
                "categorie": "driver",
                "fichiers_a_modifier": ["drivers/screen.h", "drivers/screen.c", "kernel/kernel.c"],
                "fichiers_a_creer": ["drivers/vga.h", "drivers/vga.c"],
                "fichiers_a_supprimer": [],
                "description": "Passer en mode graphique VGA mode 13h (320x200, 256 couleurs). Fonctions: vga_init(), vga_pixel(), vga_rect(), vga_clear(). Desktop coloré avec dégradé.",
                "impact_attendu": "Interface graphique colorée au lieu du mode texte VGA",
                "complexite": "HAUTE"
            },
            {
                "nom": "Terminal amélioré avec 15 commandes système",
                "priorite": "NORMALE",
                "categorie": "app",
                "fichiers_a_modifier": ["apps/terminal.h", "apps/terminal.c", "kernel/kernel.c"],
                "fichiers_a_creer": [],
                "fichiers_a_supprimer": [],
                "description": "Ajouter: ver, mem, uptime, cls, echo, date, help, reboot, halt, color, ps, kill, edit, calc, beep. Historique circulaire de 20 commandes. Autocomplétion TAB basique.",
                "impact_attendu": "Terminal puissant et interactif, expérience utilisateur améliorée",
                "complexite": "MOYENNE"
            },
        ],
        "prochaine_milestone": "Kernel stable avec IDT + Timer + Memory"
    }

# ══════════════════════════════════════════════════════════════════
# PHASE 2 : IMPLÉMENTATION
# ══════════════════════════════════════════════════════════════════
def phase_implement(task, all_sources):
    nom = task.get("nom", "Amélioration")
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

    print(f"\n[Impl] {nom}")
    print(f"[Impl] Catégorie: {categorie} | Complexité: {complexite}")
    print(f"       Modifier: {fichiers_m}")
    print(f"       Créer:    {fichiers_c}")
    print(f"       Supprimer:{fichiers_s}")

    # Contexte ciblé + fichiers liés
    lies = set(tous)
    for f in tous:
        base = f.replace(".c", "").replace(".h", "")
        for ext in [".c", ".h"]:
            candidate = base + ext
            if candidate in all_sources:
                lies.add(candidate)

    # Toujours inclure les fichiers clés
    for key in ["kernel/kernel.c", "drivers/screen.h", "drivers/screen.c",
                "drivers/keyboard.h", "ui/ui.h", "ui/ui.c", "Makefile",
                "linker.ld", "kernel/kernel_entry.asm"]:
        lies.add(key)

    ctx = "=== FICHIERS CONCERNÉS ===\n\n"
    for f in sorted(lies):
        c = all_sources.get(f, "")
        ctx += f"--- {f} ---\n{c if c else '[MANQUANT - À CRÉER]'}\n\n"

    prompt = f"""Tu es un expert OS bare metal x86. Tu développes MaxOS avec l'ambition d'atteindre la qualité de Windows 11.

{BARE_METAL_RULES}

{OS_MISSION}

CONTEXTE MAXOS ACTUEL :
{ctx}

══════════════════════════════════════════
TÂCHE : {nom}
CATÉGORIE : {categorie}
COMPLEXITÉ : {complexite}
DESCRIPTION : {desc}
IMPACT ATTENDU : {impact}
FICHIERS À MODIFIER : {fichiers_m}
FICHIERS À CRÉER : {fichiers_c}
FICHIERS À SUPPRIMER : {fichiers_s}
══════════════════════════════════════════

INSTRUCTIONS CRITIQUES :
1. Code COMPLET dans chaque fichier - JAMAIS de "// reste inchangé" ou "..."
2. Respecter EXACTEMENT les signatures existantes
3. Si tu crées de nouveaux fichiers .c, mettre à jour le Makefile
4. Si tu supprimes des fichiers, utilise la syntaxe: === DELETE: chemin ===
5. Chaque amélioration doit être visible et fonctionnelle dans QEMU
6. Penser à l'utilisateur final : rendre l'OS beau et utile
7. Documenter le code avec des commentaires /* */ explicatifs

Pour les fichiers à supprimer, utilise :
=== DELETE: chemin/fichier.c ===

Pour les fichiers à écrire, utilise :
=== FILE: chemin/fichier.c ===
[code complet]
=== END FILE ===

COMMENCE DIRECTEMENT PAR LE PREMIER FICHIER - PAS DE TEXTE INTRODUCTIF :"""

    t0 = time.time()
    max_tok = 65536 if complexite == "HAUTE" else 32768
    response = gemini(prompt, max_tokens=max_tok)
    elapsed = time.time() - t0

    if not response:
        d(f"❌ Échec: {nom}", "Gemini n'a pas répondu", 0xFF0000)
        return False, [], []

    print(f"[Impl] {len(response)} chars en {elapsed:.1f}s")

    files, to_delete = parse_files(response)

    if not files and not to_delete:
        print(f"[Debug] Début réponse:\n{response[:600]}")
        d(f"❌ Échec parse: {nom}",
          f"Aucun fichier parsé.\n```\n{response[:500]}\n```", 0xFF0000)
        return False, [], []

    print(f"[Impl] Fichiers à écrire: {list(files.keys())}")
    print(f"[Impl] Fichiers à supprimer: {to_delete}")

    backs = backup_files(list(files.keys()))
    written = write_files(files)
    deleted = delete_files([f for f in to_delete if f not in fichiers_s
                           or any(f in fichiers_s for f in to_delete)])
    deleted = delete_files(to_delete)

    if not written and not deleted:
        d(f"❌ Échec: {nom}", "Aucun fichier écrit ou supprimé", 0xFF0000)
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
        # Auto-fix
        fixed = auto_fix(log, errors, files, backs)
        if fixed:
            return True, written, deleted

        restore_files(backs)
        # Nettoyer les nouveaux fichiers créés
        for p in written:
            if p not in backs:
                fp = os.path.join(REPO_PATH, p)
                if os.path.exists(fp):
                    os.remove(fp)

        return False, [], []

# ══════════════════════════════════════════════════════════════════
# AUTO-FIX INTELLIGENT
# ══════════════════════════════════════════════════════════════════
def auto_fix(build_log, errors, generated_files, backups, max_attempts=2):
    """Correction automatique avec plusieurs tentatives."""
    print("[Fix] Correction automatique...")

    for attempt in range(1, max_attempts + 1):
        print(f"[Fix] Tentative {attempt}/{max_attempts}")

        current = {}
        for p in generated_files:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp):
                with open(fp, "r") as f:
                    current[p] = f.read()

        ctx = ""
        for p, c in current.items():
            ctx += f"--- {p} ---\n{c[:3000]}\n\n"

        error_txt = "\n".join(errors[:15])

        prompt = f"""Corrige PRÉCISÉMENT ces erreurs de compilation bare metal x86.

{BARE_METAL_RULES}

ERREURS DE COMPILATION :
```
{error_txt}
```

LOG (fin) :
```
{build_log[-2000:]}
```

FICHIERS ACTUELS :
{ctx}

RÈGLES DE CORRECTION :
- Corrige UNIQUEMENT ce qui cause les erreurs
- Code COMPLET dans chaque fichier
- Pas de librairies standard
- Vérifie les déclarations de fonctions
- Vérifie les include manquants (entre guillemets, pas <>)

=== FILE: premier_fichier_a_corriger.c ===
[code corrigé complet]
=== END FILE ==="""

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
                f"auto-fix: Correction erreurs (tentative {attempt})",
                list(files.keys()),
                f"Correction automatique: {len(errors)} erreurs → 0",
                current_model
            )
            d("🔧 Auto-correction réussie",
              f"Tentative {attempt}: {len(errors)} erreurs corrigées.",
              0x00AAFF)
            return True

        errors = new_errors
        time.sleep(10)

    restore_files(backups)
    return False

# ══════════════════════════════════════════════════════════════════
# RELEASE GITHUB PROFESSIONNELLE
# ══════════════════════════════════════════════════════════════════
def create_release(tasks_done, tasks_failed, analyse_data, stats):
    """Crée une release GitHub détaillée et professionnelle."""
    if not GITHUB_TOKEN:
        return None

    result = github_api("GET", "tags?per_page=1")
    last_tag = "v0.0.0"
    if result and len(result) > 0:
        last_tag = result[0].get("name", "v0.0.0")

    try:
        parts = [int(x) for x in last_tag.lstrip("v").split(".")]
        # Incrément intelligent : patch si peu de changements, minor si milestone
        if len(tasks_done) >= 3:
            parts[1] += 1
            parts[2] = 0
        else:
            parts[2] += 1
        new_tag = f"v{parts[0]}.{parts[1]}.{parts[2]}"
    except Exception:
        new_tag = "v1.0.0"

    now = datetime.utcnow()
    score = analyse_data.get("score_actuel", 0)
    niveau = analyse_data.get("niveau_os", "Prototype")
    milestone = analyse_data.get("prochaine_milestone", "")
    features = analyse_data.get("fonctionnalites_presentes", [])

    # Changelog détaillé
    changes_md = ""
    for t in tasks_done:
        name = t.get("nom", "?")
        files = t.get("files", [])
        sha = t.get("sha", "")
        model = t.get("model", "")
        sha_link = (f"[`{sha}`](https://github.com/{REPO_OWNER}/{REPO_NAME}/commit/{sha})"
                   if sha else "")
        changes_md += f"- **{name}** {sha_link}\n"
        if files:
            changes_md += f"  - Fichiers: `{'`, `'.join(files[:5])}`\n"
        if model:
            changes_md += f"  - Modèle IA: `{model}`\n"

    failed_md = ""
    for t in tasks_failed:
        failed_md += f"- ~~{t}~~ (reporté au prochain cycle)\n"

    features_md = "\n".join([f"  - {f}" for f in features]) or "  - Boot x86 basique"

    # Stats
    lang_stats = "\n".join([
        f"  | {ext or 'Makefile'} | {lines} lignes |"
        for ext, lines in sorted(stats.get("languages", {}).items(),
                                  key=lambda x: -x[1])[:6]
    ])

    # Clés utilisées
    keys_used = sum(1 for i in range(len(API_KEYS))
                   if KEY_STATE["usage_count"].get(i, 0) > 0)

    release_body = f"""# MaxOS {new_tag}

> **Release générée automatiquement par MaxOS AI Developer v8.0**
> Objectif final : OS à l'échelle de Windows 11, développé entièrement par IA

---

## 📊 État du projet

| Métrique | Valeur |
|----------|--------|
| Score global | {score}/100 |
| Niveau actuel | {niveau} |
| Fichiers | {stats.get('files', 0)} |
| Lignes de code | {stats.get('lines', 0):,} |
| Prochaine milestone | {milestone} |

---

## ✅ Changements de cette release

{changes_md or "- Maintenance et optimisations internes"}

{f"## ⏭ Reporté au prochain cycle{chr(10)}{failed_md}" if failed_md else ""}

---

## 🖥️ Fonctionnalités actuelles

{features_md}

---

## 📈 Statistiques du code

| Langage | Lignes |
|---------|--------|
{lang_stats}

---

## 🚀 Tester MaxOS

### Prérequis
```bash
# Ubuntu/Debian
sudo apt install qemu-system-x86

# Windows : https://www.qemu.org/windows/
# macOS
brew install qemu
```

### Option 1 — Télécharger et lancer
```bash
# Télécharger os.img depuis les artifacts GitHub Actions
# puis :
qemu-system-i386 \\
  -drive format=raw,file=os.img,if=floppy \\
  -boot a \\
  -vga std \\
  -k fr \\
  -m 32
```

### Option 2 — Compiler depuis les sources
```bash
# Installer les outils
sudo apt install nasm gcc make qemu-system-x86

# Cloner et compiler
git clone https://github.com/{REPO_OWNER}/{REPO_NAME}.git
cd MaxOS
make
make run   # Lance directement dans QEMU
```

### Option 3 — Script tout-en-un (Linux)
```bash
curl -sL https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{new_tag}/os.img -o maxos.img
qemu-system-i386 -drive format=raw,file=maxos.img,if=floppy -boot a -vga std -k fr -m 32
```

---

## ⌨️ Contrôles

| Touche | Action |
|--------|--------|
| **TAB** | Changer d'application |
| **F1** | 📝 Bloc-Notes |
| **F2** | 💻 Terminal |
| **F3** | ℹ️ Informations système |
| **F4** | 🅰️ À propos |
| **Échap** | Retour bureau |

---

## 🔧 Informations techniques

| Composant | Détail |
|-----------|--------|
| Architecture | x86 32-bit Protected Mode |
| Compilateur | GCC `-m32 -ffreestanding -nostdlib -nostdinc` |
| Assembleur | NASM ELF32 |
| Éditeur de liens | GNU LD avec script custom |
| Émulateur cible | QEMU i386 |
| IA développeur | {', '.join([ACTIVE_MODELS.get(i, {}).get('model', '?') for i in range(len(API_KEYS)) if i in ACTIVE_MODELS])} |
| Clés IA utilisées | {keys_used}/{len(API_KEYS)} |

---

## 🗺️ Roadmap

| Phase | Statut | Description |
|-------|--------|-------------|
| Phase 1 | 🔄 En cours | Fondations kernel (IDT, Timer, Mémoire) |
| Phase 2 | ⏳ Planifié | Mode graphique VESA |
| Phase 3 | ⏳ Planifié | Système de fichiers FAT12 |
| Phase 4 | ⏳ Planifié | Interface fenêtrée + souris |
| Phase 5 | ⏳ Planifié | Applications avancées |
| Phase 6 | 🌙 Futur | Stack réseau TCP/IP |

---

*Prochaine release automatique dans ~2h | Cycle #{now.strftime('%Y%m%d%H')}*
*MaxOS AI Developer v8.0 | {now.strftime('%Y-%m-%d %H:%M')} UTC*
"""

    url = github_create_release(
        tag=new_tag,
        name=f"MaxOS {new_tag} — {niveau} | {now.strftime('%Y-%m-%d')}",
        body=release_body,
        prerelease=(score < 50)
    )

    if url:
        d(
            f"🚀 Release {new_tag} publiée",
            f"Niveau : **{niveau}**\nScore : {score}/100\n{url}",
            0x00FF88,
            [
                {"name": "Version",      "value": new_tag,              "inline": True},
                {"name": "Score",        "value": f"{score}/100",       "inline": True},
                {"name": "Succès",       "value": str(len(tasks_done)), "inline": True},
                {"name": "Milestone",    "value": milestone[:50],       "inline": False},
                {"name": "Lien",         "value": f"[Voir la release]({url})", "inline": False},
            ]
        )

    return url

# ══════════════════════════════════════════════════════════════════
# RAPPORT DISCORD DÉTAILLÉ
# ══════════════════════════════════════════════════════════════════
def send_start_report(analyse):
    score = analyse.get("score_actuel", 0)
    niveau = analyse.get("niveau_os", "?")
    features = analyse.get("fonctionnalites_presentes", [])
    manquantes = analyse.get("fonctionnalites_manquantes_critiques", [])
    milestone = analyse.get("prochaine_milestone", "?")
    plan = analyse.get("plan_ameliorations", [])

    features_txt = "\n".join([f"✅ {f}" for f in features[:5]]) or "Aucune"
    manquantes_txt = "\n".join([f"❌ {f}" for f in manquantes[:5]]) or "Aucune"
    plan_txt = "\n".join([
        f"[{i+1}] [{t.get('priorite','?')}] {t.get('nom','?')}"
        for i, t in enumerate(plan[:6])
    ])

    d(
        f"🧠 Analyse MaxOS — Score {score}/100",
        f"```{progress_bar(score)}```\n**Niveau actuel:** {niveau}",
        0x00AAFF if score >= 60 else 0xFFA500 if score >= 30 else 0xFF4444,
        [
            {"name": "✅ Fonctionnalités présentes",  "value": features_txt[:512],  "inline": True},
            {"name": "🎯 À implémenter d'urgence",    "value": manquantes_txt[:512], "inline": True},
            {"name": "📋 Plan du cycle",              "value": f"```\n{plan_txt}\n```", "inline": False},
            {"name": "🏁 Prochaine milestone",        "value": milestone[:100],      "inline": False},
            {"name": "🔑 Clés Gemini",                "value": key_status_str(),     "inline": False},
        ]
    )

# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("  MaxOS AI Developer v8.0")
    print("  Objectif: OS à l'échelle de Windows 11")
    print("  Mode: Autonome 24/7 | Multi-clés | Releases automatiques")
    print("=" * 60 + "\n")

    if not find_all_models():
        print("FATAL: Aucune clé Gemini opérationnelle")
        sys.exit(1)

    current_model = ACTIVE_MODELS.get(0, {}).get("model", "?")

    d(
        "🚀 MaxOS AI Developer v8.0 démarré",
        (f"**Objectif:** OS à l'échelle de Windows 11\n"
         f"**Mode:** Autonome 24h/24 7j/7\n"
         f"**Clés actives:** {len(ACTIVE_MODELS)}/{len(API_KEYS)}"),
        0x5865F2,
        [
            {"name": "Modèles",  "value": "\n".join([
                f"Clé {i+1}: {ACTIVE_MODELS[i]['model']}"
                for i in sorted(ACTIVE_MODELS.keys())
            ]), "inline": False},
            {"name": "Repo",     "value": f"`{REPO_OWNER}/{REPO_NAME}`", "inline": True},
            {"name": "Heure",    "value": datetime.now().strftime("%H:%M:%S UTC"), "inline": True},
        ]
    )

    # Sources
    sources = read_all()
    context = build_context(sources)
    stats = get_project_stats(sources)

    print(f"[Sources] {stats['files']} fichiers, {stats['lines']} lignes, {len(context)} chars")

    # Phase 1 : Analyse
    print("\n" + "="*60)
    print(" PHASE 1 : Analyse approfondie")
    print("="*60)

    analyse = phase_analyse(context, stats)
    if not analyse:
        d("❌ Analyse échouée", "Impossible d'analyser le code.", 0xFF0000)
        sys.exit(1)

    score = analyse.get("score_actuel", 0)
    plan = analyse.get("plan_ameliorations", [])

    print(f"\n[Rapport] Score: {score}/100")
    print(f"[Rapport] Niveau: {analyse.get('niveau_os', '?')}")
    print(f"[Rapport] {len(plan)} améliorations planifiées")

    send_start_report(analyse)

    # Phase 2 : Implémentation
    print("\n" + "="*60)
    print(" PHASE 2 : Implémentation")
    print("="*60)

    order = {"CRITIQUE": 0, "HAUTE": 1, "NORMALE": 2, "BASSE": 3}
    plan_sorted = sorted(plan, key=lambda x: order.get(x.get("priorite", "NORMALE"), 2))

    success = 0
    total = len(plan_sorted)
    tasks_done = []
    tasks_failed = []

    for i, task in enumerate(plan_sorted, 1):
        nom = task.get("nom", f"Tâche {i}")
        priorite = task.get("priorite", "NORMALE")
        categorie = task.get("categorie", "?")
        complexite = task.get("complexite", "MOYENNE")

        print(f"\n{'='*60}")
        print(f" [{i}/{total}] [{priorite}] {nom}")
        print(f"{'='*60}")

        current_model = ACTIVE_MODELS.get(
            KEY_STATE["current_index"], {}
        ).get("model", "?")

        d(
            f"⚙️ [{i}/{total}] {nom}",
            f"```\n{progress_bar(int((i-1)/total*100))}\n```\n{task.get('description','')[:200]}",
            0xFFA500,
            [
                {"name": "Priorité",   "value": priorite,    "inline": True},
                {"name": "Catégorie",  "value": categorie,   "inline": True},
                {"name": "Complexité", "value": complexite,  "inline": True},
                {"name": "Modèle",     "value": current_model, "inline": True},
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
                f"✅ Succès: {nom}",
                f"Amélioration appliquée et commitée.",
                0x00FF88,
                [
                    {"name": "Fichiers écrits",     "value": "\n".join([f"`{f}`" for f in written[:5]]) or "Aucun", "inline": True},
                    {"name": "Fichiers supprimés",   "value": "\n".join([f"`{f}`" for f in deleted]) or "Aucun", "inline": True},
                    {"name": "Commit",               "value": f"`{latest_sha}`", "inline": True},
                    {"name": "Modèle utilisé",       "value": current_model, "inline": True},
                ]
            )
            # Mettre à jour les sources
            sources = read_all()
        else:
            tasks_failed.append(nom)
            d(
                f"❌ Échec: {nom}",
                "Code restauré automatiquement. Reporté au prochain cycle.",
                0xFF6600
            )

        # Pause inter-tâches (réduite si multi-clés)
        if i < total:
            pause = 15 if len(API_KEYS) > 1 else 30
            print(f"[Pause] {pause}s entre les tâches...")
            time.sleep(pause)

    # Release GitHub si succès
    if success > 0:
        print(f"\n[Release] Création de la release GitHub...")
        sources = read_all()
        stats = get_project_stats(sources)
        create_release(tasks_done, tasks_failed, analyse, stats)

    # Rapport final
    pct = int(success / total * 100) if total > 0 else 0
    color = 0x00FF88 if pct >= 80 else 0xFFA500 if pct >= 50 else 0xFF4444

    d(
        f"🏁 Cycle terminé — {success}/{total} réussies",
        (f"```\n{progress_bar(pct)}\n```\n"
         f"Prochain cycle dans ~2h (cron automatique)",
        color,
        [
            {"name": "✅ Succès",         "value": str(success),          "inline": True},
            {"name": "❌ Échecs",          "value": str(total - success),  "inline": True},
            {"name": "📊 Taux",           "value": f"{pct}%",             "inline": True},
            {"name": "🔑 Stats clés",     "value": key_status_str(),      "inline": False},
            {"name": "📝 Tâches réussies","value": "\n".join([
                f"• {t['nom'][:50]}" for t in tasks_done
            ])[:512] or "Aucune", "inline": False},
        ]
    )

    print(f"\n[FIN] {success}/{total} améliorations. Prochain cycle automatique.")

if __name__ == "__main__":
    main()
