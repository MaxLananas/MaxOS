#!/usr/bin/env python3
"""MaxOS AI Developer v8.2 - Stable, anti-ratelimit, anti-recitation"""

import os, sys, json, time, subprocess, re
import urllib.request, urllib.error
from datetime import datetime

# ══════════════════════════════════════════════════════
# CONFIGURATION
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
GITHUB_TOKEN    = os.environ.get("GITHUB_TOKEN", "")
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")
REPO_OWNER      = os.environ.get("REPO_OWNER", "MaxLananas")
REPO_NAME       = os.environ.get("REPO_NAME", "MaxOS")
REPO_PATH       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Etat global des cles
KEY_STATE = {
    "current_index":  0,
    "cooldowns":      {},   # idx -> timestamp fin cooldown
    "usage_count":    {},   # idx -> nb appels
    "errors":         {},   # idx -> nb erreurs
    "forbidden_models": {}, # idx -> set de modeles interdits (403)
}

ACTIVE_MODELS = {}  # idx -> {"model": str, "url": str}

def mask(k):
    return k[:4] + "*" * max(0, len(k)-8) + k[-4:] if len(k) > 8 else "***"

print("[v8.2] Cles: " + str(len(API_KEYS)))
for i, k in enumerate(API_KEYS):
    print("  Cle " + str(i+1) + ": " + mask(k))
print("[v8.2] Discord: " + ("OK" if DISCORD_WEBHOOK else "NON"))
print("[v8.2] GitHub:  " + ("OK" if GITHUB_TOKEN else "NON"))
print("[v8.2] Repo:    " + REPO_OWNER + "/" + REPO_NAME)

if not API_KEYS:
    print("FATAL: GEMINI_API_KEY manquante")
    sys.exit(1)

# ══════════════════════════════════════════════════════
# MODELES - ordre optimal
# gemini-2.5-flash-lite = moins de quota = moins de 429
# ══════════════════════════════════════════════════════
ALL_MODELS = [
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.5-pro",
]

# ══════════════════════════════════════════════════════
# FICHIERS CONNUS
# ══════════════════════════════════════════════════════
KNOWN_FILES = [
    "boot/boot.asm", "kernel/kernel_entry.asm", "kernel/kernel.c",
    "drivers/screen.h", "drivers/screen.c",
    "drivers/keyboard.h", "drivers/keyboard.c",
    "ui/ui.h", "ui/ui.c",
    "apps/notepad.h", "apps/notepad.c",
    "apps/terminal.h", "apps/terminal.c",
    "apps/sysinfo.h", "apps/sysinfo.c",
    "apps/about.h", "apps/about.c",
    "Makefile", "linker.ld",
]

# ══════════════════════════════════════════════════════
# REGLES BARE METAL (version courte pour les prompts)
# ══════════════════════════════════════════════════════
RULES_SHORT = """REGLES BARE METAL x86 OBLIGATOIRES:
- ZERO include standard (<stddef.h> <string.h> <stdlib.h> etc)
- ZERO types: size_t->uint, NULL->0, bool->int, true->1, false->0
- ZERO fonctions: malloc, memset, strlen, printf
- gcc -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc
- nasm -f elf / ld -m elf_i386 -T linker.ld --oformat binary
- Si nouveau .c -> mettre a jour Makefile
- L'IA peut creer, modifier, supprimer des fichiers"""

RULES_FULL = RULES_SHORT + """

SIGNATURES EXISTANTES (ne pas changer):
  nb_init(), nb_draw(), nb_key(char k)
  tm_init(), tm_draw(), tm_key(char k)
  si_draw(), ab_draw()
  kb_init(), kb_haskey(), kb_getchar()
  v_init(), v_put(), v_str(), v_fill()"""

# ══════════════════════════════════════════════════════
# MISSION (version courte)
# ══════════════════════════════════════════════════════
MISSION = """MISSION: MaxOS doit devenir un OS complet (objectif Windows 11).
Priorites: IDT+PIC > Timer PIT > Memoire > GUI graphique > Apps > Reseau.
Chaque commit doit ameliorer l'OS de facon visible dans QEMU."""

# ══════════════════════════════════════════════════════
# ROTATION DES CLES
# ══════════════════════════════════════════════════════
def get_available_key():
    """Retourne l'index de la meilleure cle disponible."""
    now = time.time()
    n = len(API_KEYS)

    # Chercher cle sans cooldown
    for delta in range(n):
        idx = (KEY_STATE["current_index"] + delta) % n
        if not API_KEYS[idx]:
            continue
        if now >= KEY_STATE["cooldowns"].get(idx, 0):
            KEY_STATE["current_index"] = idx
            KEY_STATE["usage_count"][idx] = (
                KEY_STATE["usage_count"].get(idx, 0) + 1
            )
            return idx

    # Toutes en cooldown -> attendre la moins longue
    valid = [i for i in range(n) if API_KEYS[i]]
    if not valid:
        print("[Keys] FATAL: aucune cle valide")
        sys.exit(1)

    min_idx = min(valid, key=lambda i: KEY_STATE["cooldowns"].get(i, 0))
    wait = KEY_STATE["cooldowns"].get(min_idx, 0) - now + 2
    print("[Keys] Toutes en cooldown. Attente " +
          str(int(wait)) + "s...")
    time.sleep(max(wait, 1))
    KEY_STATE["current_index"] = min_idx
    return min_idx

def cooldown_key(idx, seconds):
    """Met une cle en cooldown et bascule."""
    KEY_STATE["cooldowns"][idx] = time.time() + seconds
    KEY_STATE["errors"][idx] = KEY_STATE["errors"].get(idx, 0) + 1
    n = len(API_KEYS)
    if n > 1:
        nxt = (idx + 1) % n
        for _ in range(n):
            if API_KEYS[nxt]:
                break
            nxt = (nxt + 1) % n
        KEY_STATE["current_index"] = nxt
        print("[Keys] Cle " + str(idx+1) +
              " cooldown " + str(seconds) + "s -> cle " + str(nxt+1))
    else:
        print("[Keys] Cle " + str(idx+1) +
              " cooldown " + str(seconds) + "s")

def keys_status():
    now = time.time()
    lines = []
    for i in range(len(API_KEYS)):
        if not API_KEYS[i]:
            continue
        cd = KEY_STATE["cooldowns"].get(i, 0)
        st = "OK" if now >= cd else "CD " + str(int(cd-now)) + "s"
        m = ACTIVE_MODELS.get(i, {}).get("model", "?")
        u = KEY_STATE["usage_count"].get(i, 0)
        lines.append("Cle " + str(i+1) + ": " + st +
                     " | " + str(u) + " req | " + m)
    return "\n".join(lines)

# ══════════════════════════════════════════════════════
# INITIALISATION MODELES
# ══════════════════════════════════════════════════════
def init_key(idx):
    """Trouve le meilleur modele pour une cle."""
    if idx >= len(API_KEYS) or not API_KEYS[idx]:
        return False

    key = API_KEYS[idx]
    forbidden = KEY_STATE["forbidden_models"].get(idx, set())

    for model in ALL_MODELS:
        if model in forbidden:
            continue

        url = ("https://generativelanguage.googleapis.com/v1beta/models/" +
               model + ":generateContent?key=" + key)
        payload = json.dumps({
            "contents": [{"parts": [{"text": "Say: OK"}]}],
            "generationConfig": {"maxOutputTokens": 5, "temperature": 0}
        }).encode()

        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read())
                # Verifier qu'on a bien du texte
                parts = (data.get("candidates", [{}])[0]
                             .get("content", {})
                             .get("parts", []))
                if parts and parts[0].get("text"):
                    print("[Gemini] Cle " + str(idx+1) +
                          " -> " + model + " OK")
                    ACTIVE_MODELS[idx] = {"model": model, "url": url}
                    return True

        except urllib.error.HTTPError as e:
            print("[Gemini] Cle " + str(idx+1) +
                  " " + model + " HTTP " + str(e.code))
            if e.code == 403:
                # Ce modele est interdit pour cette cle
                if idx not in KEY_STATE["forbidden_models"]:
                    KEY_STATE["forbidden_models"][idx] = set()
                KEY_STATE["forbidden_models"][idx].add(model)
            elif e.code == 429:
                time.sleep(3)
            time.sleep(0.5)
        except Exception as e:
            print("[Gemini] Cle " + str(idx+1) + " " + model +
                  " err: " + str(e))
            time.sleep(0.5)

    print("[Gemini] Cle " + str(idx+1) + ": aucun modele dispo")
    return False

def init_all_keys():
    print("[Gemini] Init " + str(len(API_KEYS)) + " cle(s)...")
    ok = 0
    for i in range(len(API_KEYS)):
        if API_KEYS[i]:
            if init_key(i):
                ok += 1
            time.sleep(1)
    print("[Gemini] " + str(ok) + "/" + str(len(API_KEYS)) + " OK")
    return ok > 0

# ══════════════════════════════════════════════════════
# EXTRACTION TEXTE GEMINI
# ══════════════════════════════════════════════════════
def extract_text(data):
    """Extrait le texte d'une reponse Gemini (gere les thinking models)."""
    try:
        candidates = data.get("candidates", [])
        if not candidates:
            return None, "no_candidates"

        c = candidates[0]
        finish = c.get("finishReason", "STOP")

        if finish == "SAFETY":
            return None, "safety"
        if finish == "RECITATION":
            return None, "recitation"

        parts = c.get("content", {}).get("parts", [])
        if not parts:
            return None, "no_parts_" + finish

        # Concatener les parts texte (ignorer les "thought")
        texts = []
        for p in parts:
            if isinstance(p, dict) and not p.get("thought") and p.get("text"):
                texts.append(p["text"])

        result = "".join(texts)
        if not result:
            return None, "empty_text_" + finish

        return result, finish

    except Exception as e:
        return None, "parse_error_" + str(e)

# ══════════════════════════════════════════════════════
# APPEL GEMINI AVEC GESTION COMPLETE
# ══════════════════════════════════════════════════════
def call_gemini(prompt, max_tokens=32768, allow_recitation_retry=True):
    """
    Appelle Gemini avec rotation des cles.
    Gere: 429, 403, RECITATION, MAX_TOKENS, no_parts.
    """
    if not ACTIVE_MODELS:
        if not init_all_keys():
            return None

    # Limiter la taille du prompt
    if len(prompt) > 50000:
        prompt = prompt[:50000] + "\n...[TRONQUE]"

    payload_base = {
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.1,
        }
    }

    recitation_count = 0
    max_total = 4 * max(len(API_KEYS), 1)

    for attempt in range(1, max_total + 1):
        idx = get_available_key()

        if idx not in ACTIVE_MODELS:
            if not init_key(idx):
                cooldown_key(idx, 120)
                continue

        info = ACTIVE_MODELS[idx]
        url = info["url"].split("?")[0] + "?key=" + API_KEYS[idx]

        # Construire le payload
        payload = dict(payload_base)
        payload["contents"] = [{"parts": [{"text": prompt}]}]
        payload_bytes = json.dumps(payload).encode("utf-8")

        req = urllib.request.Request(
            url, data=payload_bytes,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read().decode())
                text, reason = extract_text(data)

                if text:
                    print("[Gemini] Cle " + str(idx+1) +
                          " " + info["model"] + " -> " +
                          str(len(text)) + " chars (" + reason + ")")
                    return text

                # Pas de texte
                print("[Gemini] Cle " + str(idx+1) +
                      " reponse vide: " + reason)

                if reason == "recitation" and allow_recitation_retry:
                    recitation_count += 1
                    if recitation_count <= 2:
                        # Reformuler le prompt pour eviter RECITATION
                        print("[Gemini] RECITATION -> reformulation")
                        prompt = (
                            "Implementons du code OS bare metal original.\n"
                            "NE PAS copier de code existant.\n"
                            "Ecrire une implementation unique et originale.\n\n"
                            + prompt[-3000:]  # Garder seulement la fin
                        )
                        time.sleep(5)
                        continue

                elif "MAX_TOKENS" in reason or "no_parts" in reason:
                    # Reessayer avec moins de tokens
                    if max_tokens > 8192:
                        max_tokens = max_tokens // 2
                        print("[Gemini] MAX_TOKENS -> reduit a " +
                              str(max_tokens))
                        payload_base["generationConfig"]["maxOutputTokens"] = max_tokens
                        continue

                # Essayer un autre modele
                if idx in ACTIVE_MODELS:
                    del ACTIVE_MODELS[idx]
                init_key(idx)

        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode()
            except Exception:
                pass

            print("[Gemini] Cle " + str(idx+1) +
                  " HTTP " + str(e.code) +
                  " (tentative " + str(attempt) + ")")

            if e.code == 429:
                # Rate limit -> cooldown progressif
                err_count = KEY_STATE["errors"].get(idx, 0)
                wait = min(30 + (30 * err_count), 180)
                cooldown_key(idx, wait)
                if len(API_KEYS) > 1:
                    # Rotation immediate sur autre cle
                    continue
                # Une seule cle -> attendre un peu
                time.sleep(min(wait, 60))

            elif e.code == 403:
                # Modele interdit sur cette cle
                current_model = ACTIVE_MODELS.get(idx, {}).get("model", "")
                if current_model:
                    if idx not in KEY_STATE["forbidden_models"]:
                        KEY_STATE["forbidden_models"][idx] = set()
                    KEY_STATE["forbidden_models"][idx].add(current_model)
                if idx in ACTIVE_MODELS:
                    del ACTIVE_MODELS[idx]
                # Chercher un autre modele pour cette cle
                if not init_key(idx):
                    cooldown_key(idx, 300)

            elif e.code in (400, 404):
                if idx in ACTIVE_MODELS:
                    del ACTIVE_MODELS[idx]
                init_key(idx)

            elif e.code >= 500:
                print("[Gemini] Erreur serveur " + str(e.code))
                time.sleep(30)

            else:
                time.sleep(20)

        except Exception as e:
            print("[Gemini] Exception: " + str(e))
            time.sleep(15)

    print("[Gemini] ECHEC apres " + str(max_total) + " tentatives")
    return None

# ══════════════════════════════════════════════════════
# GITHUB API
# ══════════════════════════════════════════════════════
def gh(method, endpoint, data=None):
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
            "User-Agent": "MaxOS-AI/8.2",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        print("[GitHub] " + method + " " + endpoint +
              " -> " + str(e.code))
        return None
    except Exception as e:
        print("[GitHub] " + str(e))
        return None

def gh_create_release(tag, name, body, prerelease=False):
    r = gh("POST", "releases", {
        "tag_name": tag, "name": name, "body": body,
        "draft": False, "prerelease": prerelease
    })
    if r and "html_url" in r:
        return r["html_url"]
    return None

def gh_get_prs():
    r = gh("GET", "pulls?state=open&per_page=10")
    return r if isinstance(r, list) else []

def gh_merge_pr(number, title):
    r = gh("PUT", "pulls/" + str(number) + "/merge", {
        "commit_title": "merge: " + title + " [AI]",
        "merge_method": "squash"
    })
    return bool(r and r.get("merged"))

def gh_comment(number, body):
    gh("POST", "issues/" + str(number) + "/comments", {"body": body})

def gh_close_pr(number):
    gh("PATCH", "pulls/" + str(number), {"state": "closed"})

# ══════════════════════════════════════════════════════
# DISCORD
# ══════════════════════════════════════════════════════
def discord(embeds):
    if not DISCORD_WEBHOOK:
        return
    payload = json.dumps({
        "username": "MaxOS AI Bot",
        "embeds": embeds[:10]
    }).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WEBHOOK, data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15):
            pass
    except Exception as e:
        print("[Discord] " + str(e))

def embed(title, desc, color=0x5865F2, fields=None):
    now = time.time()
    active = sum(1 for i in range(len(API_KEYS))
                 if API_KEYS[i] and now >= KEY_STATE["cooldowns"].get(i, 0))
    cur = ACTIVE_MODELS.get(KEY_STATE["current_index"], {}).get("model", "?")
    e = {
        "title": str(title)[:256],
        "description": str(desc)[:4096],
        "color": color,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "footer": {"text": (
            "MaxOS AI v8.2 | " + cur +
            " | " + str(active) + "/" + str(len(API_KEYS)) + " cles"
        )},
    }
    if fields:
        e["fields"] = fields[:25]
    return e

def d(title, desc, color=0x5865F2, fields=None):
    discord([embed(title, desc, color, fields)])

def pbar(pct, w=24):
    f = int(w * pct / 100)
    return "[" + "X"*f + "-"*(w-f) + "] " + str(pct) + "%"

# ══════════════════════════════════════════════════════
# SOURCES
# ══════════════════════════════════════════════════════
def find_files():
    """Decouvre tous les fichiers du projet."""
    found = []
    exts = {".c", ".h", ".asm", ".ld", ".py"}
    skip_dirs = {".git", "build", "__pycache__", ".github"}
    skip_files = {"screen.h.save"}
    for root, dirs, files in os.walk(REPO_PATH):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if f in skip_files:
                continue
            ext = os.path.splitext(f)[1]
            if ext in exts or f == "Makefile":
                rel = os.path.relpath(
                    os.path.join(root, f), REPO_PATH
                ).replace("\\", "/")
                found.append(rel)
    return sorted(found)

def read_sources():
    sources = {}
    all_f = list(set(KNOWN_FILES + find_files()))
    for f in sorted(all_f):
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                sources[f] = fh.read()
        else:
            sources[f] = None
    return sources

def build_context(sources, max_chars=35000):
    """Construit un contexte compact."""
    # Index
    ctx = "FICHIERS MAXOS:\n"
    for f, c in sources.items():
        ctx += ("  [OK] " if c else "  [--] ") + f + "\n"
    ctx += "\n"

    # Contenu par priorite
    priority = [
        "Makefile", "linker.ld",
        "kernel/kernel.c", "kernel/kernel_entry.asm",
        "boot/boot.asm",
        "drivers/screen.h", "drivers/keyboard.h",
        "ui/ui.h",
    ]

    chars = len(ctx)
    added = set()

    # D'abord les prioritaires
    for f in priority:
        c = sources.get(f, "")
        if not c:
            continue
        block = "=== " + f + " ===\n" + c + "\n\n"
        if chars + len(block) > max_chars:
            continue
        ctx += block
        chars += len(block)
        added.add(f)

    # Puis le reste
    for f, c in sources.items():
        if f in added or not c:
            continue
        block = "=== " + f + " ===\n" + c + "\n\n"
        if chars + len(block) > max_chars:
            ctx += "[" + f + " tronque]\n"
            continue
        ctx += block
        chars += len(block)

    return ctx

def stats(sources):
    files = sum(1 for c in sources.values() if c)
    lines = sum(c.count("\n") for c in sources.values() if c)
    return files, lines

# ══════════════════════════════════════════════════════
# GIT ET BUILD
# ══════════════════════════════════════════════════════
def git(args, cwd=None):
    r = subprocess.run(
        ["git"] + args,
        cwd=cwd or REPO_PATH,
        capture_output=True, text=True
    )
    return r.returncode == 0, r.stdout, r.stderr

def commit_msg(nom, files, desc, model):
    dirs = set()
    for f in files:
        if "/" in f:
            dirs.add(f.split("/")[0])

    prefix_map = {
        "kernel": "kernel", "drivers": "driver",
        "boot": "boot", "ui": "ui", "apps": "feat(apps)"
    }
    prefix = "feat"
    for d_name, p in prefix_map.items():
        if d_name in dirs:
            prefix = p
            break

    fshort = ", ".join(os.path.basename(f) for f in files[:3])
    if len(files) > 3:
        fshort += " +" + str(len(files)-3)

    short = prefix + ": " + nom + " [" + fshort + "]"
    body = (
        "\n\nComponent : " + ", ".join(sorted(dirs)) + "\n"
        "Files     : " + ", ".join(files) + "\n"
        "Model     : " + model + "\n"
        "Timestamp : " + datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ") + "\n"
        "\nDescription:\n  " + desc[:200] + "\n"
        "\nBuild: gcc -m32 -ffreestanding -nostdlib | nasm ELF32\n"
        "Target: x86 32-bit Protected Mode | QEMU i386"
    )
    return short, short + body

def do_push(nom, files, desc, model):
    if not files:
        return True, None, None
    short, full = commit_msg(nom, files, desc, model)
    git(["add", "-A"])
    ok, out, err = git(["commit", "-m", full])
    if not ok:
        if "nothing to commit" in (out + err):
            return True, None, None
        print("[Git] Commit KO: " + err[:150])
        return False, None, None
    _, sha, _ = git(["rev-parse", "HEAD"])
    sha = sha.strip()[:7]
    ok2, _, e2 = git(["push"])
    if not ok2:
        print("[Git] Push KO: " + e2[:150])
        return False, None, None
    print("[Git] OK " + sha + ": " + short)
    return True, sha, short

def do_build():
    subprocess.run(["make", "clean"], cwd=REPO_PATH, capture_output=True)
    r = subprocess.run(
        ["make"], cwd=REPO_PATH,
        capture_output=True, text=True, timeout=120
    )
    ok = r.returncode == 0
    log = r.stdout + r.stderr
    errors = [l.strip() for l in log.split("\n") if "error:" in l.lower()]
    print("[Build] " + ("OK" if ok else "ECHEC") +
          " (" + str(len(errors)) + " err)")
    if not ok:
        for e in errors[:5]:
            print("  " + e)
    return ok, log, errors[:12]

# ══════════════════════════════════════════════════════
# PATCH BOOTLOADER (fix "kernel trop grand")
# ══════════════════════════════════════════════════════
def fix_boot_sectors():
    """
    Recalcule et met a jour le nombre de secteurs dans boot.asm
    si le kernel a grossi.
    """
    kernel_path = os.path.join(REPO_PATH, "build", "kernel.bin")
    boot_path = os.path.join(REPO_PATH, "boot", "boot.asm")

    if not os.path.exists(kernel_path) or not os.path.exists(boot_path):
        return False

    kernel_size = os.path.getsize(kernel_path)
    sectors_needed = (kernel_size + 511) // 512
    # Ajouter marge de 10%
    sectors_with_margin = int(sectors_needed * 1.15) + 5

    print("[Boot] Kernel: " + str(kernel_size) +
          " bytes = " + str(sectors_needed) + " secteurs")
    print("[Boot] Secteurs avec marge: " + str(sectors_with_margin))

    with open(boot_path, "r") as f:
        content = f.read()

    # Chercher la ligne qui definit le nombre de secteurs
    # Patterns communs: "sectors_count equ X", "mov cx, X", "SECTORS equ X"
    patterns = [
        (r'(SECTORS\s+equ\s+)(\d+)', True),
        (r'(sectors_count\s+equ\s+)(\d+)', True),
        (r'(mov\s+cx,\s*)(\d+)', False),  # attention, peut etre autre chose
        (r'(times\s+\d+\s*-\s*\$\s+db\s+)', False),
    ]

    modified = False
    new_content = content

    # Chercher et remplacer le nombre de secteurs a charger
    # Pattern le plus commun dans les bootloaders simples
    match = re.search(r'(mov\s+cl\s*,\s*)(\d+)', content)
    if match:
        old_val = int(match.group(2))
        if sectors_with_margin > old_val:
            new_content = content[:match.start()] + \
                          match.group(1) + str(sectors_with_margin) + \
                          content[match.end():]
            modified = True
            print("[Boot] Mis a jour: mov cl, " +
                  str(old_val) + " -> " + str(sectors_with_margin))

    if not modified:
        # Chercher "SECTORS equ"
        match2 = re.search(r'(SECTORS\s+equ\s+)(\d+)', content, re.IGNORECASE)
        if match2:
            old_val = int(match2.group(2))
            if sectors_with_margin > old_val:
                new_content = content[:match2.start()] + \
                              match2.group(1) + str(sectors_with_margin) + \
                              content[match2.end():]
                modified = True
                print("[Boot] Mis a jour: SECTORS " +
                      str(old_val) + " -> " + str(sectors_with_margin))

    if modified:
        with open(boot_path, "w") as f:
            f.write(new_content)
        print("[Boot] boot.asm mis a jour")
        return True

    print("[Boot] Pattern non trouve dans boot.asm - demande a l'IA")
    return False

def check_kernel_size_and_fix():
    """
    Verifie si le kernel est trop grand pour le bootloader
    et corrige automatiquement.
    """
    boot_path = os.path.join(REPO_PATH, "build", "boot.bin")
    kernel_path = os.path.join(REPO_PATH, "build", "kernel.bin")

    if not os.path.exists(boot_path) or not os.path.exists(kernel_path):
        return True  # Pas encore compile

    kernel_size = os.path.getsize(kernel_path)
    sectors = (kernel_size + 511) // 512

    # Une disquette = 2880 secteurs, le boot prend 1
    if sectors > 2878:
        print("[Boot] ERREUR: Kernel trop grand (" +
              str(sectors) + " secteurs > 2878)")
        return False

    print("[Boot] Taille OK: " + str(sectors) + " secteurs")
    return True

# ══════════════════════════════════════════════════════
# PARSER DE FICHIERS
# ══════════════════════════════════════════════════════
def parse_response(response):
    """Parse les fichiers dans la reponse de l'IA."""
    files = {}
    to_delete = []
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
                if fname and "/" in fname or fname == "Makefile":
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
                if content.strip():
                    files[cur_file] = content
                    print("[Parse] " + cur_file +
                          " (" + str(len(content)) + " chars)")
            cur_file = None
            cur_lines = []
            in_file = False
            continue

        if "=== DELETE:" in s and s.endswith("==="):
            try:
                fname = s[s.index("=== DELETE:")+11:s.rindex("===")].strip()
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
        print("[Write] " + path + " (" + str(len(content)) + " c)")
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
            print("[Del] " + path)
    return deleted

def backup(paths):
    b = {}
    for p in paths:
        full = os.path.join(REPO_PATH, p)
        if os.path.exists(full):
            with open(full, "r", encoding="utf-8", errors="ignore") as f:
                b[p] = f.read()
    return b

def restore(backups):
    for p, c in backups.items():
        full = os.path.join(REPO_PATH, p)
        parent = os.path.dirname(full)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(c)
    print("[Restore] " + str(len(backups)) + " fichier(s)")

# ══════════════════════════════════════════════════════
# PHASE 1 : ANALYSE (prompt compact)
# ══════════════════════════════════════════════════════
def phase_analyse(sources):
    print("\n[Analyse] Debut...")
    nf, nl = stats(sources)

    # Contexte minimal pour l'analyse
    ctx = "FICHIERS: " + ", ".join(f for f, c in sources.items() if c) + "\n\n"

    # Ajouter kernel.c et Makefile seulement
    for key_file in ["kernel/kernel.c", "Makefile", "ui/ui.c",
                     "apps/terminal.c"]:
        c = sources.get(key_file, "")
        if c:
            ctx += "=== " + key_file + " ===\n" + c[:2000] + "\n\n"

    prompt = (
        RULES_SHORT + "\n\n" +
        MISSION + "\n\n" +
        ctx +
        "Stats: " + str(nf) + " fichiers, " + str(nl) + " lignes\n\n"
        "Analyse MaxOS. Reponds UNIQUEMENT en JSON valide.\n"
        "Commence par { directement:\n\n"
        '{"score":35,"niveau":"Prototype","features":["Boot x86","VGA"],'
        '"missing":["IDT","Timer"],'
        '"tasks":[{"nom":"Nom court","prio":"CRITIQUE","cat":"kernel",'
        '"modify":["kernel/kernel.c"],"create":["kernel/idt.h","kernel/idt.c"],'
        '"delete":[],"desc":"Description technique","impact":"Impact visible",'
        '"complexity":"HAUTE"}],'
        '"milestone":"Kernel stable"}'
    )

    response = call_gemini(prompt, max_tokens=3000)
    if not response:
        return None

    print("[Analyse] " + str(len(response)) + " chars")

    # Nettoyer
    clean = response.strip()
    if clean.startswith("```"):
        lines = clean.split("\n")[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        clean = "\n".join(lines).strip()

    # Nettoyer backslashes invalides
    clean = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', clean)

    for _ in range(3):
        i = clean.find("{")
        j = clean.rfind("}") + 1
        if i >= 0 and j > i:
            try:
                data = json.loads(clean[i:j])
                # Normaliser le format
                if "tasks" in data and "plan_ameliorations" not in data:
                    data["plan_ameliorations"] = []
                    for t in data["tasks"]:
                        data["plan_ameliorations"].append({
                            "nom": t.get("nom", "?"),
                            "priorite": t.get("prio", "NORMALE"),
                            "categorie": t.get("cat", "general"),
                            "fichiers_a_modifier": t.get("modify", []),
                            "fichiers_a_creer": t.get("create", []),
                            "fichiers_a_supprimer": t.get("delete", []),
                            "description": t.get("desc", ""),
                            "impact_attendu": t.get("impact", ""),
                            "complexite": t.get("complexity", "MOYENNE"),
                        })
                return data
            except json.JSONDecodeError as e:
                print("[Analyse] JSON err: " + str(e))
                clean = clean[clean.find("{"):]

    # Plan par defaut robuste
    print("[Analyse] Plan par defaut")
    return {
        "score": 30,
        "niveau": "Prototype bare metal",
        "features": ["Boot x86", "VGA texte", "Clavier", "4 apps"],
        "missing": ["IDT", "Timer PIT", "Memoire", "GUI", "FAT12"],
        "milestone": "Kernel stable",
        "plan_ameliorations": [
            {
                "nom": "IDT + PIC 8259 + exceptions x86",
                "priorite": "CRITIQUE",
                "categorie": "kernel",
                "fichiers_a_modifier": [
                    "kernel/kernel.c", "kernel/kernel_entry.asm", "Makefile"
                ],
                "fichiers_a_creer": ["kernel/idt.h", "kernel/idt.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "IDT 256 entrees. PIC 8259 remappage "
                    "(IRQ0-7 -> INT32, IRQ8-15 -> INT40). "
                    "Handlers NASM pour exceptions 0-31. "
                    "Panic screen rouge sur exception."
                ),
                "impact_attendu": "OS stable, pas de triple fault",
                "complexite": "HAUTE"
            },
            {
                "nom": "Timer PIT 8253 + sleep_ms + uptime",
                "priorite": "CRITIQUE",
                "categorie": "kernel",
                "fichiers_a_modifier": ["kernel/kernel.c", "Makefile"],
                "fichiers_a_creer": ["kernel/timer.h", "kernel/timer.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "PIT canal 0 a 100Hz (diviseur 11931). "
                    "Compteur global ticks. timer_init(), "
                    "timer_ticks(), sleep_ms(ms). "
                    "uptime dans sysinfo."
                ),
                "impact_attendu": "Horloge, animations, uptime",
                "complexite": "MOYENNE"
            },
            {
                "nom": "Terminal 20 commandes + historique fleches",
                "priorite": "HAUTE",
                "categorie": "app",
                "fichiers_a_modifier": [
                    "apps/terminal.h", "apps/terminal.c"
                ],
                "fichiers_a_creer": [],
                "fichiers_a_supprimer": [],
                "description": (
                    "Commandes: help ver mem uptime cls echo "
                    "date reboot halt color beep calc snake "
                    "about credits sysinfo ps license clear. "
                    "Historique circulaire 20 entrees (fleche haut/bas). "
                    "Prompt color avec heure."
                ),
                "impact_attendu": "Terminal type cmd.exe complet",
                "complexite": "MOYENNE"
            },
            {
                "nom": "Allocateur memoire bitmap 4KB",
                "priorite": "HAUTE",
                "categorie": "kernel",
                "fichiers_a_modifier": ["kernel/kernel.c", "Makefile"],
                "fichiers_a_creer": ["kernel/memory.h", "kernel/memory.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "Bitmap 1bit/page 4KB. Zone 1MB-16MB. "
                    "mem_init() mem_alloc() mem_free() "
                    "mem_used() mem_total(). "
                    "Stats dans sysinfo."
                ),
                "impact_attendu": "Stats memoire dans sysinfo",
                "complexite": "HAUTE"
            },
            {
                "nom": "Mode graphique VGA 320x200 + desktop",
                "priorite": "NORMALE",
                "categorie": "driver",
                "fichiers_a_modifier": [
                    "drivers/screen.h", "drivers/screen.c",
                    "kernel/kernel.c", "Makefile"
                ],
                "fichiers_a_creer": ["drivers/vga.h", "drivers/vga.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "VGA mode 13h 320x200 256 couleurs. "
                    "vga_init() vga_pixel() vga_rect() vga_text(). "
                    "Desktop degrade bleu, taskbar, icones."
                ),
                "impact_attendu": "Interface graphique coloree",
                "complexite": "HAUTE"
            },
        ]
    }

# ══════════════════════════════════════════════════════
# PHASE 2 : IMPLEMENTATION (prompt optimise)
# ══════════════════════════════════════════════════════
def implement_task(task, sources):
    nom         = task.get("nom", "Amelioration")
    cat         = task.get("categorie", "general")
    f_modify    = task.get("fichiers_a_modifier", [])
    f_create    = task.get("fichiers_a_creer", [])
    f_delete    = task.get("fichiers_a_supprimer", [])
    desc        = task.get("description", "")
    impact      = task.get("impact_attendu", "")
    complexity  = task.get("complexite", "MOYENNE")
    all_targets = list(set(f_modify + f_create))

    cur_model = ACTIVE_MODELS.get(
        KEY_STATE["current_index"], {}
    ).get("model", "?")

    print("\n[Impl] " + nom)
    print("  " + cat + " | " + complexity)
    print("  Modifier: " + str(f_modify))
    print("  Creer:    " + str(f_create))

    # Contexte cible uniquement (pas tout le projet)
    targets_ctx = ""
    already = set()

    # Fichiers directement concernes
    for f in all_targets:
        c = sources.get(f, "")
        targets_ctx += "=== " + f + " ===\n"
        targets_ctx += (c if c else "[CREER CE FICHIER]") + "\n\n"
        already.add(f)

        # Fichier .h correspondant si .c
        partner = f.replace(".c", ".h") if f.endswith(".c") else ""
        if partner and partner not in already:
            pc = sources.get(partner, "")
            if pc:
                targets_ctx += "=== " + partner + " ===\n" + pc + "\n\n"
                already.add(partner)

    # Toujours inclure kernel.c, Makefile, screen.h, keyboard.h
    for essential in ["kernel/kernel.c", "Makefile",
                      "drivers/screen.h", "drivers/keyboard.h",
                      "ui/ui.h", "linker.ld"]:
        if essential not in already:
            c = sources.get(essential, "")
            if c:
                targets_ctx += "=== " + essential + " ===\n" + c + "\n\n"
                already.add(essential)

    # Limiter la taille du contexte
    if len(targets_ctx) > 25000:
        targets_ctx = targets_ctx[:25000] + "\n...[TRONQUE]\n"

    max_tok = 49152 if complexity == "HAUTE" else 32768

    prompt = (
        RULES_FULL + "\n\n" +
        MISSION + "\n\n"
        "CONTEXTE:\n" + targets_ctx + "\n"
        "TACHE: " + nom + "\n"
        "CATEGORIE: " + cat + "\n"
        "DESCRIPTION: " + desc + "\n"
        "IMPACT: " + impact + "\n"
        "MODIFIER: " + str(f_modify) + "\n"
        "CREER: " + str(f_create) + "\n"
        "SUPPRIMER: " + str(f_delete) + "\n\n"
        "INSTRUCTIONS:\n"
        "1. Code COMPLET - jamais '// reste inchange'\n"
        "2. Nouveaux .c -> ajouter dans Makefile\n"
        "3. Pour supprimer: === DELETE: chemin ===\n"
        "4. Code original et unique\n"
        "5. Commenter avec /* */ les sections cles\n\n"
        "FORMAT:\n"
        "=== FILE: chemin/fichier.c ===\n"
        "[code complet]\n"
        "=== END FILE ===\n\n"
        "COMMENCE:"
    )

    t0 = time.time()
    response = call_gemini(prompt, max_tokens=max_tok)
    elapsed = round(time.time() - t0, 1)

    if not response:
        d("Echec: " + nom, "Gemini n'a pas repondu.", 0xFF4444)
        return False, [], []

    print("[Impl] " + str(len(response)) + " chars en " + str(elapsed) + "s")

    files, to_del = parse_response(response)

    if not files and not to_del:
        print("[Debug] " + response[:400])
        d("Echec parse: " + nom, response[:300], 0xFF4444)
        return False, [], []

    # Backup et ecriture
    bak = backup(list(files.keys()))
    written = write_files(files)
    deleted = delete_files(to_del)

    if not written and not deleted:
        return False, [], []

    # Build
    build_ok, log, errors = do_build()

    if build_ok:
        # Verifier taille kernel
        if not check_kernel_size_and_fix():
            # Kernel trop grand -> tenter fix boot
            if fix_boot_sectors():
                build_ok2, log2, errors2 = do_build()
                if not build_ok2:
                    restore(bak)
                    return False, [], []
            else:
                restore(bak)
                return False, [], []

        pushed, sha, _ = do_push(nom, written + deleted, desc, cur_model)
        if pushed:
            return True, written, deleted
        restore(bak)
        return False, [], []

    # Auto-fix
    fixed = auto_fix_errors(log, errors, files, bak, cur_model)
    if fixed:
        return True, written, deleted

    restore(bak)
    for p in written:
        if p not in bak:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp):
                os.remove(fp)
    return False, [], []

# ══════════════════════════════════════════════════════
# AUTO-FIX
# ══════════════════════════════════════════════════════
def auto_fix_errors(build_log, errors, gen_files, backups,
                    model_used, max_tries=2):
    print("[Fix] Auto-correction " + str(len(errors)) + " erreurs...")

    for attempt in range(1, max_tries + 1):
        # Lire les fichiers actuels
        current = {}
        for p in gen_files:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp):
                with open(fp, "r") as f:
                    current[p] = f.read()

        ctx = ""
        for p, c in current.items():
            ctx += "=== " + p + " ===\n" + c[:2500] + "\n\n"

        err_txt = "\n".join(errors[:10])

        prompt = (
            RULES_SHORT + "\n\n"
            "ERREURS DE COMPILATION:\n```\n" + err_txt + "\n```\n\n"
            "LOG (fin):\n```\n" + build_log[-1200:] + "\n```\n\n"
            "FICHIERS:\n" + ctx +
            "CORRIGE uniquement les erreurs. Code complet.\n\n"
            "=== FILE: fichier.c ===\n[code corrige]\n=== END FILE ==="
        )

        response = call_gemini(prompt, max_tokens=24576)
        if not response:
            continue

        files, _ = parse_response(response)
        if not files:
            continue

        write_files(files)
        ok, log, new_errors = do_build()

        if ok:
            do_push(
                "fix: correction compilation",
                list(files.keys()),
                "Auto-fix: " + str(len(errors)) + " erreurs -> 0",
                model_used
            )
            d("Auto-fix reussi",
              str(len(errors)) + " erreurs corrigees.", 0x00AAFF)
            return True

        errors = new_errors
        time.sleep(15)

    restore(backups)
    return False

# ══════════════════════════════════════════════════════
# PULL REQUESTS
# ══════════════════════════════════════════════════════
def handle_prs():
    prs = gh_get_prs()
    if not prs:
        return

    print("[PR] " + str(len(prs)) + " PR(s)")

    for pr in prs:
        num = pr.get("number")
        title = pr.get("title", "")
        author = pr.get("user", {}).get("login", "")

        # Skip les PRs du bot
        if author in ("github-actions", "MaxOS-AI-Bot"):
            continue

        files_data = gh("GET", "pulls/" + str(num) + "/files")
        if not files_data:
            continue

        file_list = "\n".join([
            "- " + f.get("filename", "") +
            " (+" + str(f.get("additions", 0)) + ")"
            for f in files_data[:10]
        ])

        prompt = (
            RULES_SHORT + "\n\n"
            "PR #" + str(num) + ": " + title + "\n"
            "Auteur: " + author + "\n"
            "Fichiers:\n" + file_list + "\n\n"
            "Decision en JSON:\n"
            '{"action":"MERGE","raison":"ok","comment":"bien"}\n'
            "MERGE si bare metal correct. REJECT si librairies standard.\n"
            "Commence par { :"
        )

        response = call_gemini(prompt, max_tokens=300)
        if not response:
            continue

        action = "REJECT"
        raison = "Analyse impossible"

        try:
            clean = response.strip()
            if clean.startswith("```"):
                clean = "\n".join(clean.split("\n")[1:])
                if clean.endswith("```"):
                    clean = clean[:-3]
            i = clean.find("{")
            j = clean.rfind("}") + 1
            if i >= 0 and j > i:
                dec = json.loads(clean[i:j])
                action = dec.get("action", "REJECT")
                raison = dec.get("raison", "")
        except Exception:
            pass

        body = ("## Review MaxOS AI v8.2\n\n"
                "**" + action + "** - " + raison + "\n\n"
                "*Review automatique*")
        gh_comment(num, body)

        if action == "MERGE":
            if gh_merge_pr(num, title):
                d("PR #" + str(num) + " mergee",
                  title + "\n" + raison, 0x00FF88)
        else:
            gh_close_pr(num)
            d("PR #" + str(num) + " rejetee",
              title + "\n" + raison, 0xFF4444)

# ══════════════════════════════════════════════════════
# RELEASE
# ══════════════════════════════════════════════════════
def make_release(tasks_done, tasks_failed, analyse, nfiles, nlines):
    if not GITHUB_TOKEN:
        return None

    # Version
    r = gh("GET", "tags?per_page=1")
    last = "v0.0.0"
    if r and len(r) > 0:
        last = r[0].get("name", "v0.0.0")
    try:
        parts = [int(x) for x in last.lstrip("v").split(".")]
        if len(tasks_done) >= 3:
            parts[1] += 1
            parts[2] = 0
        else:
            parts[2] += 1
        new_tag = "v" + ".".join(str(x) for x in parts)
    except Exception:
        new_tag = "v1.0.0"

    now = datetime.utcnow()
    score = analyse.get("score", 30)
    niveau = analyse.get("niveau", "Prototype")
    milestone = analyse.get("milestone", "")
    features = analyse.get("features", [])

    changes = ""
    for t in tasks_done:
        sha = t.get("sha", "")
        sha_link = ""
        if sha:
            sha_link = (" [`" + sha + "`](https://github.com/" +
                       REPO_OWNER + "/" + REPO_NAME + "/commit/" + sha + ")")
        changes += "- **" + t.get("nom", "") + "**" + sha_link + "\n"
        if t.get("files"):
            changes += "  - `" + "`, `".join(t["files"][:4]) + "`\n"

    failed = "".join(["- ~~" + t + "~~\n" for t in tasks_failed])

    models_used = ", ".join(set(
        ACTIVE_MODELS.get(i, {}).get("model", "")
        for i in range(len(API_KEYS)) if i in ACTIVE_MODELS
    ))

    body = (
        "# MaxOS " + new_tag + "\n\n"
        "> **MaxOS AI Developer v8.2** - Objectif: OS Windows 11 scale\n\n"
        "---\n\n"
        "## Etat\n\n"
        "| | |\n|---|---|\n"
        "| Score | **" + str(score) + "/100** |\n"
        "| Niveau | " + niveau + " |\n"
        "| Fichiers | " + str(nfiles) + " |\n"
        "| Lignes | " + str(nlines) + " |\n"
        "| Milestone | " + milestone + " |\n\n"
        "## Changements\n\n" + (changes or "- Maintenance\n") +
        ("\n## Reporte\n\n" + failed if failed else "") +
        "\n## Fonctionnalites\n\n" +
        "\n".join("- " + f for f in features) + "\n\n"
        "---\n\n"
        "## Tester MaxOS\n\n"
        "### 1. Telecharger os.img\n\n"
        "```\n"
        "GitHub -> Actions -> Dernier run -> Artifacts -> maxos-build-XXX\n"
        "```\n\n"
        "### 2. Lancer\n\n"
        "**WSL Ubuntu / Linux:**\n"
        "```bash\n"
        "sudo apt install qemu-system-x86\n"
        "qemu-system-i386 -drive format=raw,file=os.img,if=floppy "
        "-boot a -vga std -k fr -m 32 -no-reboot\n"
        "```\n\n"
        "**Windows (QEMU installe depuis qemu.org):**\n"
        "```\n"
        "qemu-system-i386.exe -drive format=raw,file=os.img,if=floppy "
        "-boot a -vga std -k fr -m 32\n"
        "```\n\n"
        "**Compiler depuis sources (WSL):**\n"
        "```bash\n"
        "sudo apt install nasm gcc make gcc-multilib qemu-system-x86\n"
        "git clone https://github.com/" + REPO_OWNER + "/" + REPO_NAME + "\n"
        "cd MaxOS && make && make run\n"
        "```\n\n"
        "## Controles\n\n"
        "| Touche | Action |\n|---|---|\n"
        "| TAB | Changer d'app |\n"
        "| F1 | Bloc-Notes |\n"
        "| F2 | Terminal |\n"
        "| F3 | Sysinfo |\n"
        "| F4 | A propos |\n\n"
        "## Technique\n\n"
        "| | |\n|---|---|\n"
        "| Arch | x86 32-bit Protected Mode |\n"
        "| CC | GCC -m32 -ffreestanding -nostdlib |\n"
        "| ASM | NASM ELF32 |\n"
        "| LD | GNU LD linker.ld |\n"
        "| QEMU | i386 |\n"
        "| IA | " + models_used + " |\n\n"
        "## Roadmap\n\n"
        "| Phase | Statut | Objectif |\n|---|---|---|\n"
        "| 1 | En cours | IDT + Timer + Memoire |\n"
        "| 2 | Planifie | Mode graphique VESA |\n"
        "| 3 | Planifie | FAT12 |\n"
        "| 4 | Planifie | GUI fenetres |\n"
        "| 5 | Planifie | Applications |\n"
        "| 6 | Futur | TCP/IP |\n\n"
        "*MaxOS AI v8.2 | " + now.strftime("%Y-%m-%d %H:%M") + " UTC*\n"
    )

    url = gh_create_release(
        new_tag,
        "MaxOS " + new_tag + " - " + niveau + " | " + now.strftime("%Y-%m-%d"),
        body,
        prerelease=(score < 50)
    )

    if url:
        d("Release " + new_tag,
          "Score: " + str(score) + "/100 | " + niveau,
          0x00FF88,
          [
              {"name": "Version", "value": new_tag, "inline": True},
              {"name": "Score",   "value": str(score) + "/100", "inline": True},
              {"name": "Succes",  "value": str(len(tasks_done)), "inline": True},
              {"name": "Lien",
               "value": "[Release](" + url + ")", "inline": False},
          ])
    return url

# ══════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════
def main():
    print("=" * 55)
    print("  MaxOS AI Developer v8.2")
    print("  OS echelle Windows 11 | Autonome 24/7")
    print("=" * 55 + "\n")

    # Init cles
    if not init_all_keys():
        print("FATAL: Aucune cle operationnelle")
        sys.exit(1)

    cur_model = ACTIVE_MODELS.get(0, {}).get("model", "?")

    d("MaxOS AI v8.2 demarre",
      "Cles: " + str(len(ACTIVE_MODELS)) + "/" + str(len(API_KEYS)) +
      " | Objectif: Windows 11 scale",
      0x5865F2,
      [
          {"name": "Cles actives",
           "value": "\n".join([
               "Cle " + str(i+1) + ": " + ACTIVE_MODELS[i]["model"]
               for i in sorted(ACTIVE_MODELS.keys())
           ]) or "?",
           "inline": False},
          {"name": "Repo",
           "value": REPO_OWNER + "/" + REPO_NAME, "inline": True},
      ])

    # PRs
    print("\n[PRs] Verification...")
    handle_prs()

    # Sources
    sources = read_sources()
    nf, nl = stats(sources)
    print("[Sources] " + str(nf) + " fichiers, " + str(nl) + " lignes")

    # Analyse
    print("\n" + "="*55 + "\n PHASE 1: Analyse\n" + "="*55)
    analyse = phase_analyse(sources)
    if not analyse:
        d("Analyse echouee", "Impossible d'analyser.", 0xFF0000)
        sys.exit(1)

    score = analyse.get("score", 30)
    niveau = analyse.get("niveau", "?")
    plan = analyse.get("plan_ameliorations", [])
    milestone = analyse.get("milestone", "?")
    features = analyse.get("features", [])
    missing = analyse.get("missing", [])

    print("[Analyse] Score: " + str(score) + "/100 | " + niveau)
    print("[Analyse] " + str(len(plan)) + " taches | " + milestone)

    d("Score " + str(score) + "/100 - " + niveau,
      "```\n" + pbar(score) + "\n```",
      0x00AAFF if score >= 60 else 0xFFA500 if score >= 30 else 0xFF4444,
      [
          {"name": "Presentes",
           "value": "\n".join(["+ " + f for f in features[:4]]) or "?",
           "inline": True},
          {"name": "Manquantes",
           "value": "\n".join(["- " + f for f in missing[:4]]) or "?",
           "inline": True},
          {"name": "Plan (" + str(len(plan)) + " taches)",
           "value": "\n".join([
               "[" + str(i+1) + "] [" + t.get("priorite","?") + "] " +
               t.get("nom","?")[:40]
               for i, t in enumerate(plan[:5])
           ]),
           "inline": False},
          {"name": "Milestone", "value": milestone[:80], "inline": False},
          {"name": "Cles", "value": keys_status(), "inline": False},
      ])

    # Implementation
    print("\n" + "="*55 + "\n PHASE 2: Implementation\n" + "="*55)

    order = {"CRITIQUE": 0, "HAUTE": 1, "NORMALE": 2, "BASSE": 3}
    plan_sorted = sorted(
        plan,
        key=lambda x: order.get(x.get("priorite", "NORMALE"), 2)
    )

    success = 0
    total = len(plan_sorted)
    done = []
    failed = []

    for i, task in enumerate(plan_sorted, 1):
        nom = task.get("nom", "Tache " + str(i))
        prio = task.get("priorite", "NORMALE")
        cat = task.get("categorie", "?")

        print("\n" + "="*55)
        print("[" + str(i) + "/" + str(total) + "] [" + prio + "] " + nom)
        print("="*55)

        cur = ACTIVE_MODELS.get(
            KEY_STATE["current_index"], {}
        ).get("model", "?")

        d("[" + str(i) + "/" + str(total) + "] " + nom,
          "```\n" + pbar(int((i-1)/total*100)) + "\n```\n" +
          task.get("description", "")[:150],
          0xFFA500,
          [
              {"name": "Priorite",  "value": prio, "inline": True},
              {"name": "Categorie", "value": cat,  "inline": True},
              {"name": "Modele",    "value": cur,  "inline": True},
          ])

        sources = read_sources()
        ok, written, deleted = implement_task(task, sources)

        _, sha_raw, _ = git(["rev-parse", "HEAD"])
        sha = sha_raw.strip()[:7] if sha_raw.strip() else "?"

        if ok:
            success += 1
            done.append({
                "nom": nom, "sha": sha,
                "files": written + deleted,
                "model": cur,
            })
            d("Succes: " + nom, "Commit `" + sha + "`", 0x00FF88,
              [
                  {"name": "Ecrits",
                   "value": "\n".join(["`" + f + "`"
                                      for f in written[:4]]) or "Aucun",
                   "inline": True},
                  {"name": "Supprimes",
                   "value": "\n".join(["`" + f + "`"
                                      for f in deleted]) or "Aucun",
                   "inline": True},
              ])
            sources = read_sources()
        else:
            failed.append(nom)
            d("Echec: " + nom, "Code restaure.", 0xFF6600)

        if i < total:
            # Pause intelligente: plus courte si multi-cles
            n_active = sum(
                1 for i2 in range(len(API_KEYS))
                if API_KEYS[i2] and
                time.time() >= KEY_STATE["cooldowns"].get(i2, 0)
            )
            pause = 10 if n_active > 1 else 25
            print("[Pause] " + str(pause) + "s...")
            time.sleep(pause)

    # Release
    if success > 0:
        print("\n[Release] Creation...")
        sources = read_sources()
        nf2, nl2 = stats(sources)
        make_release(done, failed, analyse, nf2, nl2)

    # Final
    pct = int(success / total * 100) if total > 0 else 0
    color = 0x00FF88 if pct >= 80 else 0xFFA500 if pct >= 50 else 0xFF4444

    d("Cycle fini - " + str(success) + "/" + str(total),
      "```\n" + pbar(pct) + "\n```",
      color,
      [
          {"name": "Succes",  "value": str(success),       "inline": True},
          {"name": "Echecs",  "value": str(total-success), "inline": True},
          {"name": "Taux",    "value": str(pct) + "%",     "inline": True},
          {"name": "Cles",    "value": keys_status(),      "inline": False},
          {"name": "Taches",
           "value": "\n".join(
               ["OK: " + t["nom"][:40] for t in done] +
               ["KO: " + t[:40] for t in failed]
           )[:400] or "?",
           "inline": False},
      ])

    print("\n[FIN] " + str(success) + "/" + str(total))

if __name__ == "__main__":
    main()
