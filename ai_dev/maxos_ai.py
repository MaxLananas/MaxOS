#!/usr/bin/env python3
"""
MaxOS AI Developer v10.0
========================
Basé sur v9.1 | Refonte complète

NOUVEAUTÉS v10.0:
  - Fix critique: détection erreurs build élargie (fatal:, ld:, make:, nasm:)
  - Fix auto_fix: log mis à jour entre tentatives
  - Fix auto_fix: fichiers non tronqués à 2500 chars (→ 8000)
  - Gestion Issues GitHub (triage, réponse, label, close/reopen)
  - Discussion PR enrichie: commentaires inline sur lignes précises
  - Milestone GitHub: création + assignation automatique
  - Project board: création de cards pour les tâches
  - Branch protection: vérification avant merge
  - Checks/Status: création de commit statuses
  - Labels intelligents: création auto + assignation
  - Stale bot: détection et fermeture des issues inactives
  - Wiki GitHub: mise à jour automatique de la doc
  - Changelog automatique entre releases
  - Analyse de dépendances circulaires
  - Score de qualité de code détaillé
  - Rate limit GitHub suivi en temps réel
  - Retry exponentiel Gemini amélioré
  - Métriques détaillées par tâche (temps, tokens, tentatives)
  - Rapport final Discord ultra-détaillé
  - Watchdog: détection de boucles infinies
  - Cache contexte source pour éviter re-lectures inutiles
  - Mode DEBUG avec logs verbeux
  - Nettoyage artefacts de build obsolètes
"""

import os, sys, json, time, subprocess, re, hashlib, traceback
import urllib.request, urllib.error
from datetime import datetime, timezone

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION GLOBALE
# ══════════════════════════════════════════════════════════════════════════════

VERSION      = "10.0"
DEBUG        = os.environ.get("MAXOS_DEBUG", "0") == "1"
START_TIME   = time.time()

def load_api_keys():
    keys = []
    k1 = os.environ.get("GEMINI_API_KEY", "")
    if k1: keys.append(k1)
    for i in range(2, 10):
        k = os.environ.get("GEMINI_API_KEY_" + str(i), "")
        if k: keys.append(k)
    return keys

API_KEYS        = load_api_keys()
GITHUB_TOKEN    = os.environ.get("GH_PAT", "") or os.environ.get("GITHUB_TOKEN", "")
DISCORD_WEBHOOK = os.environ.get("DISCORD_WEBHOOK", "")
REPO_OWNER      = os.environ.get("REPO_OWNER", "MaxLananas")
REPO_NAME       = os.environ.get("REPO_NAME", "MaxOS")
REPO_PATH       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Modèles Gemini ─────────────────────────────────────────────────────────
MODELS_PRIORITY = [
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-1.5-flash-latest",
]

# ── État global clés ────────────────────────────────────────────────────────
KEY_STATE = {
    "current_index": 0,
    "cooldowns":     {},   # idx -> timestamp fin cooldown
    "usage_count":   {},   # idx -> nb appels totaux
    "errors":        {},   # idx -> nb erreurs
    "forbidden":     {},   # idx -> set(modeles interdits)
    "tokens_used":   {},   # idx -> nb tokens estimés
}
ACTIVE_MODELS = {}  # idx -> {"model": str, "url": str}

# ── Métriques par tâche ─────────────────────────────────────────────────────
TASK_METRICS = []  # liste de dicts par tâche

# ── Cache source ─────────────────────────────────────────────────────────────
SOURCE_CACHE = {"hash": None, "data": None}

# ── Rate limit GitHub ───────────────────────────────────────────────────────
GH_RATE = {"remaining": 5000, "reset": 0, "last_check": 0}

def log(msg, level="INFO"):
    ts = datetime.now(timezone.utc).strftime("%H:%M:%S")
    prefix = {"INFO": "", "DEBUG": "[DBG] ", "WARN": "[!] ", "ERROR": "[ERR] "}.get(level, "")
    if level == "DEBUG" and not DEBUG:
        return
    print(f"[{ts}] {prefix}{msg}")

def mask_key(k):
    return k[:4] + "*" * max(0, len(k)-8) + k[-4:] if len(k) > 8 else "***"

def uptime_str():
    s = int(time.time() - START_TIME)
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

# ── Affichage bannière ──────────────────────────────────────────────────────
print("=" * 60)
print(f"  MaxOS AI Developer v{VERSION}")
print(f"  Gemini-2.5-flash | GitHub API complète | Issues + PRs")
print("=" * 60)
print(f"[v{VERSION}] {len(API_KEYS)} clé(s) Gemini")
for i, k in enumerate(API_KEYS):
    print(f"  Clé {i+1}: {mask_key(k)}")
print(f"[v{VERSION}] Discord: {'OK' if DISCORD_WEBHOOK else 'ABSENT'}")
print(f"[v{VERSION}] GitHub:  {'OK' if GITHUB_TOKEN else 'NON'}")
print(f"[v{VERSION}] Repo:    {REPO_OWNER}/{REPO_NAME}")

if not API_KEYS:
    print("FATAL: GEMINI_API_KEY manquante")
    sys.exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# MISSION & RÈGLES BARE METAL
# ══════════════════════════════════════════════════════════════════════════════

OS_MISSION = """MISSION MAXOS - OBJECTIF OS COMPLET TYPE WINDOWS 11
L'IA est développeur principal autonome 24h/24.
L'IA PEUT: créer, modifier, supprimer n'importe quel fichier.

PRIORITÉS:
1. IDT 256 entrées + PIC 8259 (IRQ remappés)
2. Timer PIT 8253 100Hz + sleep_ms + uptime
3. Mémoire physique bitmap 4KB
4. Mode graphique VGA mode 13h (320x200)
5. Terminal 20+ commandes + historique
6. Système fichiers FAT12
7. GUI fenêtres + souris
8. Réseau TCP/IP"""

BARE_METAL_RULES = """RÈGLES BARE METAL x86 ABSOLUES:
ZERO: #include <stddef.h|string.h|stdlib.h|stdio.h|stdint.h|stdbool.h>
ZERO: size_t NULL bool true false uint32_t malloc memset strlen printf
REMPLACER: size_t->unsigned int, NULL->0, bool->int, true->1, false->0
COMPILER: gcc -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie
ASM: nasm -f elf (.o) ou nasm -f bin (boot.bin)
LD: ld -m elf_i386 -T linker.ld --oformat binary
Nouveaux .c -> OBLIGATOIRE dans Makefile
SIGNATURES: nb_init() nb_draw() nb_key(char k)
            tm_init() tm_draw() tm_key(char k)
            si_draw() ab_draw()
            kb_init() kb_haskey() kb_getchar()
            v_init() v_put() v_str() v_fill()"""

# ══════════════════════════════════════════════════════════════════════════════
# FICHIERS DU PROJET
# ══════════════════════════════════════════════════════════════════════════════

ALL_FILES = [
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

SKIP_DIRS  = {".git", "build", "__pycache__", ".github", "ai_dev"}
SKIP_FILES = {"screen.h.save"}
SRC_EXTS   = {".c", ".h", ".asm", ".ld"}

# ══════════════════════════════════════════════════════════════════════════════
# ROTATION DES CLÉS GEMINI
# ══════════════════════════════════════════════════════════════════════════════

def get_best_key():
    """Sélectionne la clé disponible. Attend si toutes en cooldown."""
    now = time.time()
    n = len(API_KEYS)
    for delta in range(n):
        idx = (KEY_STATE["current_index"] + delta) % n
        if API_KEYS[idx] and now >= KEY_STATE["cooldowns"].get(idx, 0):
            KEY_STATE["current_index"] = idx
            KEY_STATE["usage_count"][idx] = KEY_STATE["usage_count"].get(idx, 0) + 1
            return idx
    valid = [i for i in range(n) if API_KEYS[i]]
    if not valid:
        print("FATAL: Aucune clé valide")
        sys.exit(1)
    best  = min(valid, key=lambda i: KEY_STATE["cooldowns"].get(i, 0))
    wait  = KEY_STATE["cooldowns"].get(best, 0) - now + 1
    log(f"[Keys] Toutes en cooldown. Attente {int(wait)}s...")
    time.sleep(max(wait, 1))
    KEY_STATE["current_index"] = best
    return best

def set_cooldown(idx, secs):
    KEY_STATE["cooldowns"][idx] = time.time() + secs
    KEY_STATE["errors"][idx] = KEY_STATE["errors"].get(idx, 0) + 1
    n = len(API_KEYS)
    if n > 1:
        nxt = (idx + 1) % n
        for _ in range(n):
            if API_KEYS[nxt]: break
            nxt = (nxt + 1) % n
        KEY_STATE["current_index"] = nxt
        log(f"[Keys] Clé {idx+1} cooldown {secs}s -> clé {nxt+1}")
    else:
        log(f"[Keys] Clé 1 cooldown {secs}s")

def key_status():
    now   = time.time()
    lines = []
    for i in range(len(API_KEYS)):
        if not API_KEYS[i]: continue
        cd  = KEY_STATE["cooldowns"].get(i, 0)
        st  = "OK" if now >= cd else f"CD+{int(cd-now)}s"
        m   = ACTIVE_MODELS.get(i, {}).get("model", "?")
        c   = KEY_STATE["usage_count"].get(i, 0)
        lines.append(f"Clé {i+1}: {st} | {c} appels | {m}")
    return "\n".join(lines) or "Aucune clé"

# ══════════════════════════════════════════════════════════════════════════════
# INIT MODÈLES
# ══════════════════════════════════════════════════════════════════════════════

def find_model_for_key(idx):
    """Teste et trouve le meilleur modèle pour une clé."""
    if idx >= len(API_KEYS) or not API_KEYS[idx]:
        return False
    key      = API_KEYS[idx]
    forbidden = KEY_STATE["forbidden"].get(idx, set())
    for model in MODELS_PRIORITY:
        if model in forbidden:
            continue
        url     = (f"https://generativelanguage.googleapis.com/v1beta/models/"
                   f"{model}:generateContent?key={key}")
        payload = json.dumps({
            "contents": [{"parts": [{"text": "Reply: OK"}]}],
            "generationConfig": {"maxOutputTokens": 5, "temperature": 0.0}
        }).encode()
        req = urllib.request.Request(url, data=payload,
                                     headers={"Content-Type": "application/json"},
                                     method="POST")
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read())
                text = extract_text(data)
                if text is not None:
                    log(f"[Init] Clé {idx+1} -> {model} OK")
                    ACTIVE_MODELS[idx] = {"model": model, "url": url}
                    return True
                else:
                    log(f"[Init] Clé {idx+1} {model} réponse vide")
        except urllib.error.HTTPError as e:
            if e.code == 403:
                forbidden.add(model)
                KEY_STATE["forbidden"][idx] = forbidden
                log(f"[Init] Clé {idx+1} {model} interdit (403)")
            elif e.code == 429:
                log(f"[Init] Clé {idx+1} {model} rate limit")
                time.sleep(3)
            elif e.code == 404:
                forbidden.add(model)
                KEY_STATE["forbidden"][idx] = forbidden
            time.sleep(0.5)
        except Exception as ex:
            log(f"[Init] Clé {idx+1} {model}: {ex}", "DEBUG")
            time.sleep(0.5)
    log(f"[Init] Clé {idx+1}: aucun modèle disponible")
    return False

def find_all_models():
    """Init lazy: configure sans appels de test."""
    log("[Init] Init lazy (sans appels test)...")
    ok = 0
    for i in range(len(API_KEYS)):
        if not API_KEYS[i]: continue
        forbidden = KEY_STATE["forbidden"].get(i, set())
        for model in MODELS_PRIORITY:
            if model not in forbidden:
                ACTIVE_MODELS[i] = {
                    "model": model,
                    "url": (
                        "https://generativelanguage.googleapis.com"
                        f"/v1beta/models/{model}:generateContent?key={API_KEYS[i]}"
                    )
                }
                log(f"[Init] Clé {i+1} -> {model} (lazy)")
                ok += 1
                break
    log(f"[Init] {ok}/{len(API_KEYS)} clés configurées")
    return ok > 0

# ══════════════════════════════════════════════════════════════════════════════
# EXTRACTION TEXTE GEMINI
# ══════════════════════════════════════════════════════════════════════════════

def extract_text(data):
    """Extrait le texte d'une réponse Gemini. Gère tous les cas."""
    try:
        cands = data.get("candidates", [])
        if not cands:
            return None
        c      = cands[0]
        finish = c.get("finishReason", "STOP")
        if finish in ("SAFETY", "RECITATION"):
            log(f"[Gemini] Bloqué: {finish}", "WARN")
            return None
        parts = c.get("content", {}).get("parts", [])
        if not parts:
            t = c.get("content", {}).get("text", "")
            return t if t else None
        texts = []
        for p in parts:
            if isinstance(p, dict) and not p.get("thought"):
                t = p.get("text", "")
                if t: texts.append(t)
        result = "".join(texts)
        return result if result else None
    except Exception as e:
        log(f"[Extract] Erreur: {e}", "ERROR")
        return None

# ══════════════════════════════════════════════════════════════════════════════
# APPEL GEMINI AVEC RETRY EXPONENTIEL
# ══════════════════════════════════════════════════════════════════════════════

def gemini(prompt, max_tokens=32768, timeout=90, context_tag="?"):
    """
    Appel Gemini avec:
    - Retry exponentiel adaptatif
    - Rotation de clés et de modèles
    - Métriques de tokens estimées
    - Tag de contexte pour logs lisibles
    """
    if not ACTIVE_MODELS:
        if not find_all_models():
            return None

    # Troncature du prompt si trop long
    if len(prompt) > 52000:
        prompt = prompt[:52000] + "\n[TRONQUÉ - contexte trop long]"

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": 0.05,
        }
    }).encode("utf-8")

    max_attempts = len(API_KEYS) * 3

    for attempt in range(1, max_attempts + 1):
        idx = get_best_key()

        if idx not in ACTIVE_MODELS:
            if not find_model_for_key(idx):
                set_cooldown(idx, 120)
                continue

        model_info = ACTIVE_MODELS[idx]
        key        = API_KEYS[idx]
        url        = model_info["url"].split("?")[0] + "?key=" + key

        log(f"[Gemini/{context_tag}] Clé {idx+1}/{model_info['model']} "
            f"attempt={attempt} timeout={timeout}s")

        req = urllib.request.Request(
            url, data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        try:
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw  = r.read().decode("utf-8")
                data = json.loads(raw)

            elapsed = round(time.time() - t0, 1)
            text    = extract_text(data)

            if text is None:
                log(f"[Gemini/{context_tag}] Réponse vide/bloquée en {elapsed}s", "WARN")
                forbidden = KEY_STATE["forbidden"].setdefault(idx, set())
                forbidden.add(model_info["model"])
                if idx in ACTIVE_MODELS:
                    del ACTIVE_MODELS[idx]
                find_model_for_key(idx)
                continue

            finish = ""
            try:
                finish = data["candidates"][0].get("finishReason", "STOP")
            except Exception:
                pass

            # Estimation tokens (4 chars ≈ 1 token)
            est_tokens = len(text) // 4
            KEY_STATE["tokens_used"][idx] = (
                KEY_STATE["tokens_used"].get(idx, 0) + est_tokens
            )

            log(f"[Gemini/{context_tag}] OK {len(text)} chars en {elapsed}s "
                f"(finish={finish}, ~{est_tokens}tk)")
            return text

        except urllib.error.HTTPError as e:
            elapsed = round(time.time() - t0, 1)
            log(f"[Gemini/{context_tag}] HTTP {e.code} clé={idx+1} en {elapsed}s", "WARN")

            if e.code == 429:
                errs      = KEY_STATE["errors"].get(idx, 0)
                wait      = min(30 * (errs + 1), 120)
                set_cooldown(idx, wait)
                now = time.time()
                autre_dispo = any(
                    API_KEYS[i] and now >= KEY_STATE["cooldowns"].get(i, 0)
                    for i in range(len(API_KEYS)) if i != idx
                )
                if not autre_dispo:
                    sleep_time = min(wait, 45)
                    log(f"[Gemini] Attente {sleep_time}s...")
                    time.sleep(sleep_time)

            elif e.code == 403:
                forbidden = KEY_STATE["forbidden"].setdefault(idx, set())
                forbidden.add(model_info["model"])
                log(f"[Gemini] Modèle {model_info['model']} interdit clé {idx+1}", "WARN")
                if idx in ACTIVE_MODELS:
                    del ACTIVE_MODELS[idx]
                if not find_model_for_key(idx):
                    set_cooldown(idx, 600)

            elif e.code in (400, 404):
                if idx in ACTIVE_MODELS:
                    del ACTIVE_MODELS[idx]
                find_model_for_key(idx)

            elif e.code == 500:
                time.sleep(20)
            else:
                time.sleep(15)

        except TimeoutError:
            log(f"[Gemini/{context_tag}] TIMEOUT {timeout}s clé={idx+1}", "WARN")
            KEY_STATE["current_index"] = (idx + 1) % len(API_KEYS)

        except Exception as ex:
            log(f"[Gemini/{context_tag}] Exception: {ex}", "ERROR")
            if DEBUG: traceback.print_exc()
            time.sleep(10)

    log(f"[Gemini/{context_tag}] ÉCHEC après {max_attempts} tentatives", "ERROR")
    return None

# ══════════════════════════════════════════════════════════════════════════════
# DISCORD
# ══════════════════════════════════════════════════════════════════════════════

def discord_send(embeds):
    if not DISCORD_WEBHOOK:
        return False
    payload = json.dumps({
        "username": "MaxOS AI Bot",
        "embeds":   embeds[:10]
    }).encode("utf-8")
    req = urllib.request.Request(
        DISCORD_WEBHOOK, data=payload,
        headers={"Content-Type": "application/json",
                 "User-Agent":   "MaxOS-Bot/" + VERSION},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status in (200, 204)
    except urllib.error.HTTPError as e:
        body = ""
        try: body = e.read().decode()[:200]
        except: pass
        log(f"[Discord] HTTP {e.code}: {body}", "WARN")
        if e.code == 401:
            log("[Discord] WEBHOOK INVALIDE!", "ERROR")
    except Exception as ex:
        log(f"[Discord] {ex}", "WARN")
    return False

def make_embed(title, desc, color, fields=None):
    now    = time.time()
    active = sum(1 for i in range(len(API_KEYS))
                 if API_KEYS[i] and now >= KEY_STATE["cooldowns"].get(i, 0))
    cur_model = ACTIVE_MODELS.get(
        KEY_STATE["current_index"], {}
    ).get("model", "?")
    e = {
        "title":       str(title)[:256],
        "description": str(desc)[:4096],
        "color":       color,
        "timestamp":   datetime.utcnow().isoformat() + "Z",
        "footer": {"text": (
            f"MaxOS AI v{VERSION} | {cur_model} | "
            f"{active}/{len(API_KEYS)} clés | uptime {uptime_str()}"
        )}
    }
    if fields:
        e["fields"] = [
            {"name":   str(f.get("name",""))[:256],
             "value":  str(f.get("value","?"))[:1024],
             "inline": bool(f.get("inline", False))}
            for f in fields[:25]
        ]
    return e

def d(title, desc="", color=0x5865F2, fields=None):
    discord_send([make_embed(title, desc, color, fields)])

def pbar(pct, w=28):
    f = int(w * pct / 100)
    return "[" + "X"*f + "-"*(w-f) + "] " + str(pct) + "%"

# ══════════════════════════════════════════════════════════════════════════════
# GITHUB API — COUCHE COMPLÈTE
# ══════════════════════════════════════════════════════════════════════════════

def github_api(method, endpoint, data=None, raw_url=None, retry=3):
    """
    Appel GitHub API avec:
    - Retry automatique sur 5xx
    - Suivi du rate limit
    - Support URL absolue (raw_url)
    - Timeout adaptatif
    """
    if not GITHUB_TOKEN:
        return None

    url = raw_url or (
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/{endpoint}"
    )
    payload = json.dumps(data).encode() if data else None

    for attempt in range(1, retry + 1):
        req = urllib.request.Request(
            url, data=payload,
            headers={
                "Authorization":        "Bearer " + GITHUB_TOKEN,
                "Accept":               "application/vnd.github+json",
                "Content-Type":         "application/json",
                "User-Agent":           "MaxOS-AI-Bot/" + VERSION,
                "X-GitHub-Api-Version": "2022-11-28",
            },
            method=method
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                # Mise à jour rate limit
                remaining = r.headers.get("X-RateLimit-Remaining")
                reset_ts  = r.headers.get("X-RateLimit-Reset")
                if remaining:
                    GH_RATE["remaining"] = int(remaining)
                if reset_ts:
                    GH_RATE["reset"] = int(reset_ts)
                if GH_RATE["remaining"] < 100:
                    log(f"[GitHub] Rate limit bas: {GH_RATE['remaining']} restants", "WARN")
                body = r.read().decode()
                return json.loads(body) if body else {}

        except urllib.error.HTTPError as e:
            body = ""
            try: body = e.read().decode()[:400]
            except: pass
            log(f"[GitHub] {method} {endpoint} HTTP {e.code} (attempt {attempt}): {body[:100]}", "WARN")
            if e.code in (500, 502, 503, 504) and attempt < retry:
                time.sleep(5 * attempt)
                continue
            if e.code == 403 and "rate limit" in body.lower():
                wait = max(GH_RATE["reset"] - time.time() + 5, 60)
                log(f"[GitHub] Rate limit - attente {int(wait)}s...")
                time.sleep(wait)
                continue
            return None

        except Exception as ex:
            log(f"[GitHub] Exception {method} {endpoint}: {ex}", "ERROR")
            if attempt < retry:
                time.sleep(3)
                continue
            return None

    return None

def github_get_all(endpoint, per_page=100):
    """Récupère toutes les pages d'un endpoint paginé."""
    results = []
    page    = 1
    while True:
        sep = "&" if "?" in endpoint else "?"
        r   = github_api("GET", f"{endpoint}{sep}per_page={per_page}&page={page}")
        if not isinstance(r, list) or not r:
            break
        results.extend(r)
        if len(r) < per_page:
            break
        page += 1
    return results

# ── Helpers PR ──────────────────────────────────────────────────────────────

def gh_open_prs():
    r = github_api("GET", "pulls?state=open&per_page=20")
    return r if isinstance(r, list) else []

def gh_pr_files(num):
    r = github_api("GET", f"pulls/{num}/files?per_page=50")
    return r if isinstance(r, list) else []

def gh_pr_commits(num):
    r = github_api("GET", f"pulls/{num}/commits?per_page=50")
    return r if isinstance(r, list) else []

def gh_pr_reviews(num):
    r = github_api("GET", f"pulls/{num}/reviews")
    return r if isinstance(r, list) else []

def gh_merge(num, title):
    r = github_api("PUT", f"pulls/{num}/merge", {
        "commit_title":  f"merge: {title} [AI]",
        "merge_method": "squash"
    })
    return bool(r and r.get("merged"))

def gh_close_pr(num):
    github_api("PATCH", f"pulls/{num}", {"state": "closed"})

def gh_post_comment(num, body):
    github_api("POST", f"issues/{num}/comments", {"body": body})

def gh_post_pr_review(num, body, event="COMMENT", comments=None):
    """
    Poste une review PR avec commentaires inline optionnels.
    event: COMMENT | APPROVE | REQUEST_CHANGES
    comments: [{"path": "file.c", "line": 42, "body": "..."}]
    """
    payload = {
        "body":  body,
        "event": event,
    }
    if comments:
        payload["comments"] = [
            {
                "path":     c.get("path", ""),
                "line":     c.get("line", 1),
                "side":     "RIGHT",
                "body":     c.get("body", ""),
            }
            for c in comments if c.get("path") and c.get("body")
        ]
    return github_api("POST", f"pulls/{num}/reviews", payload)

def gh_request_changes(num, body, comments=None):
    return gh_post_pr_review(num, body, "REQUEST_CHANGES", comments)

def gh_approve_pr(num, body):
    return gh_post_pr_review(num, body, "APPROVE")

# ── Helpers Issues ──────────────────────────────────────────────────────────

def gh_open_issues(labels=None, since=None):
    """Récupère les issues ouvertes, avec filtres optionnels."""
    params = "issues?state=open&per_page=30"
    if labels:
        params += "&labels=" + ",".join(labels)
    if since:
        params += f"&since={since}"
    r = github_api("GET", params)
    if not isinstance(r, list):
        return []
    # Exclure les PRs (GitHub les liste aussi comme issues)
    return [i for i in r if not i.get("pull_request")]

def gh_get_issue(num):
    return github_api("GET", f"issues/{num}")

def gh_close_issue(num, reason="completed"):
    """reason: completed | not_planned | reopened"""
    github_api("PATCH", f"issues/{num}", {
        "state":         "closed",
        "state_reason":  reason
    })

def gh_reopen_issue(num):
    github_api("PATCH", f"issues/{num}", {"state": "open"})

def gh_post_issue_comment(num, body):
    github_api("POST", f"issues/{num}/comments", {"body": body})

def gh_add_labels_to_issue(num, labels):
    github_api("POST", f"issues/{num}/labels", {"labels": labels})

def gh_remove_label_from_issue(num, label):
    github_api("DELETE", f"issues/{num}/labels/{urllib.request.quote(label, safe='')}")

def gh_assign_issue(num, assignees):
    github_api("POST", f"issues/{num}/assignees", {"assignees": assignees})

def gh_lock_issue(num, reason="off-topic"):
    """reason: off-topic | too heated | resolved | spam"""
    github_api("PUT", f"issues/{num}/lock", {"lock_reason": reason})

def gh_issue_timeline(num):
    """Récupère la timeline d'une issue (commentaires, events)."""
    r = github_api("GET", f"issues/{num}/timeline?per_page=50")
    return r if isinstance(r, list) else []

# ── Helpers Labels ──────────────────────────────────────────────────────────

def gh_list_labels():
    r = github_api("GET", "labels?per_page=100")
    return {l["name"]: l for l in (r if isinstance(r, list) else [])}

def gh_ensure_labels(desired):
    """
    Crée les labels manquants.
    desired: dict {"label_name": "couleur_hex_sans_#"}
    """
    existing = gh_list_labels()
    for name, color in desired.items():
        if name not in existing:
            github_api("POST", "labels", {
                "name":  name,
                "color": color,
                "description": f"[MaxOS AI] {name}"
            })
            log(f"[Labels] Créé: {name}")

STANDARD_LABELS = {
    "ai-reviewed":    "0075ca",
    "ai-approved":    "0e8a16",
    "ai-rejected":    "b60205",
    "needs-fix":      "e4e669",
    "bug":            "d73a4a",
    "enhancement":    "a2eeef",
    "question":       "d876e3",
    "duplicate":      "cfd3d7",
    "wontfix":        "ffffff",
    "help wanted":    "008672",
    "good first issue":"7057ff",
    "stale":          "eeeeee",
    "kernel":         "5319e7",
    "driver":         "1d76db",
    "app":            "0052cc",
    "documentation":  "0075ca",
    "performance":    "e99695",
    "security":       "ee0701",
}

# ── Helpers Milestones ──────────────────────────────────────────────────────

def gh_list_milestones():
    r = github_api("GET", "milestones?state=open&per_page=30")
    return r if isinstance(r, list) else []

def gh_create_milestone(title, description="", due_on=None):
    payload = {"title": title, "description": description}
    if due_on:
        payload["due_on"] = due_on
    r = github_api("POST", "milestones", payload)
    return r.get("number") if r else None

def gh_ensure_milestone(title):
    """Retourne le numéro du milestone existant ou en crée un."""
    milestones = gh_list_milestones()
    for m in milestones:
        if m.get("title") == title:
            return m.get("number")
    return gh_create_milestone(title, f"[MaxOS AI] {title}")

def gh_assign_milestone(issue_num, milestone_num):
    github_api("PATCH", f"issues/{issue_num}", {"milestone": milestone_num})

# ── Helpers Releases ────────────────────────────────────────────────────────

def gh_create_release(tag, name, body, pre=False, draft=False):
    r = github_api("POST", "releases", {
        "tag_name":   tag,
        "name":       name,
        "body":       body,
        "draft":      draft,
        "prerelease": pre,
    })
    return r.get("html_url") if r and "html_url" in r else None

def gh_list_releases(n=10):
    r = github_api("GET", f"releases?per_page={n}")
    return r if isinstance(r, list) else []

def gh_latest_release():
    r = github_api("GET", "releases/latest")
    return r if r else {}

# ── Helpers Commits / Stats ─────────────────────────────────────────────────

def gh_commits_since(sha=None, since_hours=24):
    """Commits depuis un SHA ou depuis N heures."""
    if sha:
        r = github_api("GET", f"commits?sha={sha}&per_page=50")
    else:
        since = datetime.utcnow()
        since_str = since.strftime("%Y-%m-%dT%H:%M:%SZ")
        r = github_api("GET", f"commits?since={since_str}&per_page=50")
    return r if isinstance(r, list) else []

def gh_compare(base, head):
    """Compare deux refs, retourne les commits et fichiers entre eux."""
    r = github_api("GET", f"compare/{base}...{head}")
    return r if r else {}

# ── Helpers Commit Status ───────────────────────────────────────────────────

def gh_create_commit_status(sha, state, description, context="maxos-ai/build"):
    """
    Crée un statut de commit.
    state: error | failure | pending | success
    """
    github_api("POST", f"statuses/{sha}", {
        "state":       state,
        "description": description[:140],
        "context":     context,
    })

# ── Helpers Search ──────────────────────────────────────────────────────────

def gh_search_issues(query, issue_type="issue"):
    """Recherche dans les issues/PRs du repo."""
    q   = f"{query} repo:{REPO_OWNER}/{REPO_NAME} type:{issue_type}"
    url = f"https://api.github.com/search/issues?q={urllib.request.quote(q)}&per_page=20"
    r   = github_api("GET", "", raw_url=url)
    return r.get("items", []) if r else []

# ══════════════════════════════════════════════════════════════════════════════
# GIT LOCAL
# ══════════════════════════════════════════════════════════════════════════════

def git_cmd(args, cwd=None):
    r = subprocess.run(
        ["git"] + args,
        cwd=cwd or REPO_PATH,
        capture_output=True, text=True, timeout=60
    )
    return r.returncode == 0, r.stdout, r.stderr

def git_push(task_name, files_written, description, model_used):
    if not files_written:
        return True, None, None

    dirs   = set(f.split("/")[0] for f in files_written if "/" in f)
    pmap   = {"kernel":"kernel","drivers":"driver","boot":"boot",
               "ui":"ui","apps":"feat(apps)","lib":"lib"}
    prefix = next((pmap[d] for d in pmap if d in dirs), "feat")

    fshort = ", ".join(os.path.basename(f) for f in files_written[:4])
    if len(files_written) > 4:
        fshort += f" +{len(files_written)-4}"

    short = f"{prefix}: {task_name[:50]} [{fshort}]"
    body  = (
        f"\n\nComponent : {', '.join(sorted(dirs))}\n"
        f"Files     : {', '.join(files_written)}\n"
        f"Model     : {model_used}\n"
        f"Timestamp : {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"\nDescription:\n  {description[:200]}\n"
        f"\narch: x86-32 | gcc -m32 -ffreestanding | nasm ELF32"
    )

    git_cmd(["add", "-A"])
    ok, out, err = git_cmd(["commit", "-m", short + body])
    if not ok:
        if "nothing to commit" in (out + err):
            log("[Git] Rien à committer")
            return True, None, None
        log(f"[Git] Commit KO: {err[:200]}", "ERROR")
        return False, None, None

    _, sha, _ = git_cmd(["rev-parse", "HEAD"])
    sha = sha.strip()[:7]

    ok2, _, e2 = git_cmd(["push"])
    if not ok2:
        git_cmd(["pull", "--rebase"])
        ok2, _, e2 = git_cmd(["push"])
        if not ok2:
            log(f"[Git] Push KO: {e2[:200]}", "ERROR")
            return False, None, None

    log(f"[Git] {sha}: {short}")
    return True, sha, short

def get_current_sha():
    _, sha, _ = git_cmd(["rev-parse", "HEAD"])
    return sha.strip()[:40] if sha.strip() else ""

# ══════════════════════════════════════════════════════════════════════════════
# BUILD — DÉTECTION ÉLARGIE DES ERREURS (FIX CRITIQUE v10)
# ══════════════════════════════════════════════════════════════════════════════

# Patterns d'erreur reconnus
BUILD_ERROR_PATTERNS = [
    r"error:",           # gcc, g++, clang
    r"fatal error:",     # gcc fatal
    r"fatal:",           # nasm, ld
    r"undefined reference",    # ld linker
    r"cannot find",      # ld, gcc
    r"no such file",     # includes manquants
    r"\*\*\* \[",        # make errors: *** [target] Error N
    r"Error \d+$",       # make exit codes
    r"FAILED$",          # make FAILED
    r"nasm:.*error",     # nasm
    r"ld:.*error",       # linker
    r"collect2: error",  # gcc collect2
    r"linker command failed",  # clang linker
    r"multiple definition",    # duplicate symbols
    r"duplicate symbol",       # clang
]

BUILD_ERROR_RE = re.compile(
    "|".join(BUILD_ERROR_PATTERNS), re.IGNORECASE
)

def parse_build_errors(log_text):
    """Extrait toutes les erreurs de build, peu importe le format."""
    errors = []
    for line in log_text.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if BUILD_ERROR_RE.search(stripped):
            errors.append(stripped[:120])
    # Déduplique en préservant l'ordre
    seen = set()
    unique = []
    for e in errors:
        if e not in seen:
            seen.add(e)
            unique.append(e)
    return unique[:20]

def make_build():
    """Nettoie et recompile. Retourne (ok, log_complet, liste_erreurs)."""
    subprocess.run(["make", "clean"], cwd=REPO_PATH,
                   capture_output=True, timeout=30)
    r = subprocess.run(
        ["make"], cwd=REPO_PATH,
        capture_output=True, text=True, timeout=120
    )
    ok   = r.returncode == 0
    log_text = r.stdout + r.stderr
    errs = parse_build_errors(log_text)

    status = "OK" if ok else f"ÉCHEC ({len(errs)} erreur(s))"
    log(f"[Build] {status}")
    for e in errs[:5]:
        log(f"  >> {e[:100]}")

    return ok, log_text, errs

# ══════════════════════════════════════════════════════════════════════════════
# SOURCES DU PROJET
# ══════════════════════════════════════════════════════════════════════════════

def discover_files():
    found = []
    for root, dirs, files in os.walk(REPO_PATH):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f in SKIP_FILES: continue
            ext = os.path.splitext(f)[1]
            if ext in SRC_EXTS or f == "Makefile":
                rel = os.path.relpath(
                    os.path.join(root, f), REPO_PATH
                ).replace("\\", "/")
                found.append(rel)
    return sorted(found)

def read_all(force=False):
    """Lit tous les fichiers source avec cache basé sur hash du répertoire."""
    all_files = sorted(set(ALL_FILES + discover_files()))

    # Hash rapide basé sur mtimes
    h = hashlib.md5()
    for f in all_files:
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            h.update(str(os.path.getmtime(p)).encode())
    current_hash = h.hexdigest()

    if not force and SOURCE_CACHE["hash"] == current_hash and SOURCE_CACHE["data"]:
        log("[Sources] Cache hit", "DEBUG")
        return SOURCE_CACHE["data"]

    sources = {}
    for f in all_files:
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    sources[f] = fh.read()
            except:
                sources[f] = None
        else:
            sources[f] = None

    SOURCE_CACHE["hash"] = current_hash
    SOURCE_CACHE["data"] = sources
    return sources

def build_context(sources, max_chars=42000):
    ctx  = "=== CODE SOURCE MAXOS ===\n\nFICHIERS:\n"
    for f, c in sources.items():
        ctx += "  " + ("[OK] " if c else "[--] ") + f + "\n"
    ctx  += "\n"
    used  = len(ctx)

    prio = [
        "kernel/kernel.c", "kernel/kernel_entry.asm",
        "Makefile", "linker.ld",
        "drivers/screen.h", "drivers/keyboard.h",
        "ui/ui.h", "ui/ui.c",
    ]
    done = set()

    for f in prio:
        c = sources.get(f, "")
        if not c: continue
        block = "=" * 50 + f"\nFICHIER: {f}\n" + "=" * 50 + "\n" + c + "\n\n"
        if used + len(block) > max_chars: continue
        ctx += block; used += len(block); done.add(f)

    for f, c in sources.items():
        if f in done or not c: continue
        block = "=" * 50 + f"\nFICHIER: {f}\n" + "=" * 50 + "\n" + c + "\n\n"
        if used + len(block) > max_chars:
            ctx += f"[{f} tronqué]\n"
            continue
        ctx += block; used += len(block)

    return ctx

def proj_stats(sources):
    files = sum(1 for c in sources.values() if c)
    lines = sum(c.count("\n") for c in sources.values() if c)
    total_chars = sum(len(c) for c in sources.values() if c)
    return {"files": files, "lines": lines, "chars": total_chars}

# ══════════════════════════════════════════════════════════════════════════════
# PARSER DE FICHIERS GÉNÉRÉS PAR L'IA
# ══════════════════════════════════════════════════════════════════════════════

def parse_files(response):
    """
    Parse la réponse de l'IA pour extraire les fichiers.
    Format: === FILE: chemin === ... === END FILE ===
    Gère aussi les balises DELETE.
    """
    files   = {}
    to_del  = []
    cur     = None
    lines   = []
    in_file = False

    for line in response.split("\n"):
        s = line.strip()

        # Détection ouverture de fichier
        if "=== FILE:" in s and s.endswith("==="):
            try:
                fname = s[s.index("=== FILE:")+9:s.rindex("===")].strip().strip("`").strip()
                if fname:
                    cur     = fname
                    lines   = []
                    in_file = True
            except:
                pass
            continue

        # Détection fermeture de fichier
        if s == "=== END FILE ===" and in_file:
            if cur:
                content = "\n".join(lines).strip()
                # Strip les balises markdown de code
                for lang in ["```c","```asm","```nasm","```makefile","```ld",
                             "```bash","```text","```"]:
                    if content.startswith(lang):
                        content = content[len(lang):].lstrip("\n")
                        break
                if content.endswith("```"):
                    content = content[:-3].rstrip("\n")
                if content.strip():
                    files[cur] = content.strip()
                    log(f"[Parse] {cur} ({len(content)} chars)")
            cur     = None
            lines   = []
            in_file = False
            continue

        # Détection suppression
        if "=== DELETE:" in s and s.endswith("==="):
            try:
                fname = s[s.index("=== DELETE:")+11:s.rindex("===")].strip()
                if fname:
                    to_del.append(fname)
                    log(f"[Parse] DELETE: {fname}")
            except:
                pass
            continue

        if in_file:
            lines.append(line)

    # Debug si rien parsé
    if not files and not to_del and response:
        log(f"[Parse] Rien trouvé. Début réponse:\n{response[:300]}", "DEBUG")

    return files, to_del

def write_files(files):
    written = []
    for path, content in files.items():
        if path.startswith("/") or ".." in path: continue
        full = os.path.join(REPO_PATH, path)
        os.makedirs(os.path.dirname(full) or REPO_PATH, exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        written.append(path)
        log(f"[Write] {path}")
    # Invalide le cache après écriture
    SOURCE_CACHE["hash"] = None
    return written

def delete_files(paths):
    deleted = []
    for path in paths:
        if path.startswith("/") or ".." in path: continue
        full = os.path.join(REPO_PATH, path)
        if os.path.exists(full):
            os.remove(full)
            deleted.append(path)
            log(f"[Del] {path}")
    SOURCE_CACHE["hash"] = None
    return deleted

def backup_files(paths):
    bak = {}
    for p in paths:
        full = os.path.join(REPO_PATH, p)
        if os.path.exists(full):
            with open(full, "r", encoding="utf-8", errors="ignore") as f:
                bak[p] = f.read()
    return bak

def restore_files(bak):
    for p, c in bak.items():
        full = os.path.join(REPO_PATH, p)
        os.makedirs(os.path.dirname(full) or REPO_PATH, exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="\n") as f:
            f.write(c)
    if bak:
        log(f"[Restore] {len(bak)} fichier(s)")
    SOURCE_CACHE["hash"] = None

# ══════════════════════════════════════════════════════════════════════════════
# ANALYSE DE QUALITÉ DE CODE
# ══════════════════════════════════════════════════════════════════════════════

def analyze_code_quality(sources):
    """
    Analyse statique rapide du code source.
    Détecte les violations des règles bare metal et retourne un score.
    """
    violations = []
    forbidden_includes = [
        "stddef.h","string.h","stdlib.h","stdio.h",
        "stdint.h","stdbool.h","stdarg.h","limits.h"
    ]
    forbidden_symbols = [
        "size_t", "NULL", "bool", "true", "false",
        "uint32_t", "uint8_t", "int32_t",
        "malloc", "free", "memset", "memcpy", "strlen",
        "printf", "sprintf", "scanf"
    ]

    total_lines  = 0
    c_files      = 0
    asm_files    = 0
    violation_count = 0

    for fname, content in sources.items():
        if not content:
            continue
        if fname.endswith(".c") or fname.endswith(".h"):
            c_files += 1
            lines = content.split("\n")
            total_lines += len(lines)
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith("//") or stripped.startswith("/*"):
                    continue
                for inc in forbidden_includes:
                    if f"#include <{inc}>" in line or f'#include "{inc}"' in line:
                        violations.append(f"{fname}:{i} - include interdit: {inc}")
                        violation_count += 1
                for sym in forbidden_symbols:
                    pattern = r'\b' + re.escape(sym) + r'\b'
                    if re.search(pattern, line):
                        violations.append(f"{fname}:{i} - symbole interdit: {sym}")
                        violation_count += 1
                        break  # Une violation par ligne suffit
        elif fname.endswith(".asm"):
            asm_files += 1
            total_lines += content.count("\n")

    score = max(0, 100 - violation_count * 5)
    return {
        "score":           score,
        "violations":      violations[:20],
        "violation_count": violation_count,
        "c_files":         c_files,
        "asm_files":       asm_files,
        "total_lines":     total_lines,
    }

def detect_circular_deps(sources):
    """Détecte les dépendances circulaires entre headers."""
    deps = {}
    for fname, content in sources.items():
        if not content or not (fname.endswith(".c") or fname.endswith(".h")):
            continue
        includes = re.findall(r'#include\s+"([^"]+)"', content)
        deps[fname] = set(includes)

    # Détection de cycles simple (DFS)
    circles = []
    visited = set()

    def dfs(node, path):
        if node in path:
            cycle_start = path.index(node)
            circles.append(" -> ".join(path[cycle_start:]) + f" -> {node}")
            return
        if node in visited:
            return
        visited.add(node)
        for dep in deps.get(node, set()):
            # Normaliser le chemin
            for key in deps:
                if key.endswith(dep) or dep.endswith(os.path.basename(key)):
                    dfs(key, path + [node])

    for f in deps:
        dfs(f, [])

    return circles[:5]  # Max 5 cycles

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1: ANALYSE DU PROJET
# ══════════════════════════════════════════════════════════════════════════════

def phase_analyse(context, stats):
    """Analyse complète du projet et génère un plan d'amélioration."""
    log("\n[Phase 1] Analyse en cours...")

    prompt = (
        "Tu es un expert OS bare metal x86.\n\n" +
        BARE_METAL_RULES + "\n\n" +
        OS_MISSION + "\n\n" +
        context + "\n\n"
        f"STATS: {stats['files']} fichiers, {stats['lines']} lignes, "
        f"{stats.get('chars',0)} chars\n\n"
        "Retourne UNIQUEMENT ce JSON (commence par {, rien avant):\n\n"
        "{\n"
        '  "score_actuel": 35,\n'
        '  "niveau_os": "Prototype bare metal",\n'
        '  "fonctionnalites_presentes": ["Boot x86", "VGA texte"],\n'
        '  "fonctionnalites_manquantes_critiques": ["IDT", "Timer PIT"],\n'
        '  "plan_ameliorations": [\n'
        '    {\n'
        '      "nom": "IDT + PIC 8259",\n'
        '      "priorite": "CRITIQUE",\n'
        '      "categorie": "kernel",\n'
        '      "fichiers_a_modifier": ["kernel/kernel.c"],\n'
        '      "fichiers_a_creer": ["kernel/idt.h", "kernel/idt.c"],\n'
        '      "fichiers_a_supprimer": [],\n'
        '      "description": "Détails techniques précis",\n'
        '      "impact_attendu": "Visible dans QEMU",\n'
        '      "complexite": "HAUTE"\n'
        '    }\n'
        '  ],\n'
        '  "prochaine_milestone": "Kernel stable"\n'
        "}"
    )

    resp = gemini(prompt, max_tokens=3500, timeout=60, context_tag="analyse")
    if not resp:
        log("[Phase 1] Gemini KO -> plan par défaut", "WARN")
        return default_plan()

    log(f"[Phase 1] {len(resp)} chars reçus")

    clean = resp.strip()
    if clean.startswith("```"):
        lines = clean.split("\n")[1:]
        if lines and lines[-1].strip() == "```": lines = lines[:-1]
        clean = "\n".join(lines).strip()

    clean = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', clean)

    for _ in range(3):
        i = clean.find("{")
        j = clean.rfind("}") + 1
        if i >= 0 and j > i:
            try:
                return json.loads(clean[i:j])
            except json.JSONDecodeError as e:
                log(f"[Phase 1] JSON err: {e}", "DEBUG")
                clean = clean[i+1:]

    return default_plan()

def default_plan():
    """Plan par défaut si l'analyse échoue."""
    return {
        "score_actuel": 30,
        "niveau_os": "Prototype bare metal",
        "fonctionnalites_presentes": [
            "Boot x86", "VGA texte", "Clavier PS/2", "4 apps"
        ],
        "fonctionnalites_manquantes_critiques": [
            "IDT", "Timer PIT", "Mémoire", "Mode graphique", "FAT12"
        ],
        "prochaine_milestone": "Kernel stable IDT+Timer",
        "plan_ameliorations": [
            {
                "nom": "IDT 256 entrées + PIC 8259 + handlers",
                "priorite": "CRITIQUE", "categorie": "kernel",
                "fichiers_a_modifier": [
                    "kernel/kernel.c", "kernel/kernel_entry.asm", "Makefile"
                ],
                "fichiers_a_creer": ["kernel/idt.h", "kernel/idt.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "IDT 256 entrées. PIC 8259 remappage IRQ0-7->32-39. "
                    "Stubs NASM vecteurs 0-47. Handlers exceptions 0-31. "
                    "panic() écran rouge. sti() à la fin de kernel_main."
                ),
                "impact_attendu": "OS stable, plus de triple fault",
                "complexite": "HAUTE"
            },
            {
                "nom": "Timer PIT 8253 100Hz + uptime + sleep_ms",
                "priorite": "CRITIQUE", "categorie": "kernel",
                "fichiers_a_modifier": ["kernel/kernel.c", "Makefile"],
                "fichiers_a_creer": ["kernel/timer.h", "kernel/timer.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "PIT canal 0 diviseur 11931=100Hz. "
                    "ticks volatile unsigned int. "
                    "timer_init() timer_ticks() sleep_ms(ms). "
                    "Uptime HH:MM:SS dans sysinfo."
                ),
                "impact_attendu": "Horloge système, uptime visible",
                "complexite": "MOYENNE"
            },
            {
                "nom": "Terminal 20 commandes + historique flèches",
                "priorite": "HAUTE", "categorie": "app",
                "fichiers_a_modifier": ["apps/terminal.h", "apps/terminal.c"],
                "fichiers_a_creer": [],
                "fichiers_a_supprimer": [],
                "description": (
                    "20 commandes: help ver mem uptime cls echo date "
                    "reboot halt color beep calc snake pong about "
                    "credits clear ps sysinfo license. "
                    "Historique 20 entrées flèche haut/bas."
                ),
                "impact_attendu": "Terminal complet type cmd.exe",
                "complexite": "MOYENNE"
            },
            {
                "nom": "Allocateur mémoire bitmap pages 4KB",
                "priorite": "HAUTE", "categorie": "kernel",
                "fichiers_a_modifier": ["kernel/kernel.c", "Makefile"],
                "fichiers_a_creer": ["kernel/memory.h", "kernel/memory.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "Bitmap 32MB / 4KB = 8192 bits. "
                    "mem_init(start, end) mem_alloc() mem_free(addr). "
                    "ZERO stdlib - juste outb/inb et pointeurs bruts."
                ),
                "impact_attendu": "Allocation dynamique sans malloc",
                "complexite": "HAUTE"
            },
            {
                "nom": "Mode VGA 320x200 256 couleurs + desktop",
                "priorite": "NORMALE", "categorie": "driver",
                "fichiers_a_modifier": [
                    "drivers/screen.h", "drivers/screen.c",
                    "kernel/kernel.c", "Makefile"
                ],
                "fichiers_a_creer": ["drivers/vga.h", "drivers/vga.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "INT 10h AH=0 AL=0x13 pour entrer mode 13h. "
                    "Framebuffer à 0xA0000. v_pixel(x,y,c) v_rect() v_line(). "
                    "Desktop background bleu + taskbar grise en bas."
                ),
                "impact_attendu": "Interface graphique basique",
                "complexite": "HAUTE"
            }
        ]
    }

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2: IMPLÉMENTATION D'UNE TÂCHE
# ══════════════════════════════════════════════════════════════════════════════

def phase_implement(task, all_sources):
    """
    Implémente une tâche d'amélioration.
    Retourne (ok, fichiers_écrits, fichiers_supprimés, métriques).
    """
    nom       = task.get("nom", "?")
    categorie = task.get("categorie", "general")
    f_mod     = task.get("fichiers_a_modifier", [])
    f_new     = task.get("fichiers_a_creer", [])
    f_del     = task.get("fichiers_a_supprimer", [])
    desc      = task.get("description", "")
    impact    = task.get("impact_attendu", "")
    cx        = task.get("complexite", "MOYENNE")
    targets   = list(set(f_mod + f_new))

    model   = ACTIVE_MODELS.get(KEY_STATE["current_index"], {}).get("model", "?")
    t_start = time.time()

    log(f"\n[Impl] {nom}")
    log(f"  Cat={categorie} Cx={cx}")
    log(f"  Mod={f_mod}")
    log(f"  New={f_new}")

    # Contexte ciblé: fichiers à toucher + leurs .h/.c partenaires
    needed = set(targets)
    for f in targets:
        partner = f.replace(".c", ".h") if f.endswith(".c") else f.replace(".h", ".c")
        if partner in all_sources: needed.add(partner)
    for ess in ["kernel/kernel.c", "kernel/kernel_entry.asm",
                "drivers/screen.h", "drivers/keyboard.h",
                "ui/ui.h", "Makefile", "linker.ld"]:
        needed.add(ess)

    ctx       = "=== FICHIERS CONCERNÉS ===\n\n"
    total_len = 0
    for f in sorted(needed):
        c     = all_sources.get(f, "")
        block = f"--- {f} ---\n" + (c if c else "[À CRÉER]") + "\n\n"
        if total_len + len(block) > 22000:
            ctx += f"[{f} - trop grand, tronqué]\n"
            continue
        ctx       += block
        total_len += len(block)

    # Tokens selon complexité
    tok     = {"HAUTE": 32768, "MOYENNE": 20480, "BASSE": 12288}
    max_tok = tok.get(cx, 20480)

    prompt = (
        "Tu es un expert OS bare metal x86.\n" +
        BARE_METAL_RULES + "\n\n" +
        OS_MISSION + "\n\n" +
        ctx + "\n"
        f"TÂCHE: {nom}\n"
        f"CATÉGORIE: {categorie} | COMPLEXITÉ: {cx}\n"
        f"DESCRIPTION: {desc}\n"
        f"IMPACT: {impact}\n"
        f"MODIFIER: {f_mod}\n"
        f"CRÉER: {f_new}\n"
        f"SUPPRIMER: {f_del}\n\n"
        "INSTRUCTIONS:\n"
        "1. Code COMPLET - JAMAIS '// reste inchangé' ou '...'\n"
        "2. Respecter TOUTES les règles bare metal\n"
        "3. Nouveaux .c -> ajouter dans Makefile\n"
        "4. Supprimer: === DELETE: chemin ===\n"
        "5. Tester mentalement que ça compile\n\n"
        "FORMAT OBLIGATOIRE:\n"
        "=== FILE: chemin/fichier.ext ===\n"
        "[code complet]\n"
        "=== END FILE ===\n\n"
        "COMMENCE:"
    )

    resp    = gemini(prompt, max_tokens=max_tok, timeout=120, context_tag=f"impl/{nom[:20]}")
    elapsed = round(time.time() - t_start, 1)

    if not resp:
        d(f"❌ Échec: {nom[:50]}",
          f"Gemini n'a pas répondu après {elapsed}s",
          0xFF4444)
        return False, [], [], {"nom": nom, "elapsed": elapsed, "result": "gemini_fail"}

    log(f"[Impl] {len(resp)} chars en {elapsed}s")

    files, to_del = parse_files(resp)

    if not files and not to_del:
        d(f"⚠️ Parse vide: {nom[:50]}",
          "Réponse reçue mais rien parsé.", 0xFFA500)
        return False, [], [], {"nom": nom, "elapsed": elapsed, "result": "parse_empty"}

    bak     = backup_files(list(files.keys()))
    written = write_files(files)
    deleted = delete_files(to_del)

    if not written and not deleted:
        return False, [], [], {"nom": nom, "elapsed": elapsed, "result": "no_files"}

    ok, build_log, errs = make_build()

    if ok:
        pushed, sha, _ = git_push(nom, written + deleted, desc, model)
        if pushed:
            metrics = {
                "nom":     nom,
                "elapsed": round(time.time() - t_start, 1),
                "result":  "success",
                "sha":     sha,
                "files":   written + deleted,
                "model":   model,
            }
            return True, written, deleted, metrics
        restore_files(bak)
        return False, [], [], {"nom": nom, "elapsed": elapsed, "result": "push_fail"}

    # ── Auto-fix si build échoue ─────────────────────────────────────────────
    fixed, fix_metrics = auto_fix(build_log, errs, files, bak, model)
    if fixed:
        metrics = {
            "nom":       nom,
            "elapsed":   round(time.time() - t_start, 1),
            "result":    "success_after_fix",
            "files":     written + deleted,
            "model":     model,
            "fix_count": fix_metrics.get("attempts", 0),
        }
        return True, written, deleted, metrics

    # Restauration complète
    restore_files(bak)
    for p in written:
        if p not in bak:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp): os.remove(fp)
    SOURCE_CACHE["hash"] = None

    return False, [], [], {
        "nom":     nom,
        "elapsed": round(time.time() - t_start, 1),
        "result":  "build_fail",
        "errors":  errs[:5],
    }

# ══════════════════════════════════════════════════════════════════════════════
# AUTO-FIX — VERSION CORRIGÉE v10
# FIX: log mis à jour entre tentatives
# FIX: fichiers lus en entier (8000 chars, pas 2500)
# FIX: contexte d'erreur enrichi avec diff
# ══════════════════════════════════════════════════════════════════════════════

def auto_fix(build_log, errs, gen_files, bak, model, max_attempts=2):
    """
    Tente de corriger les erreurs de build.
    Retourne (ok, métriques).
    """
    log(f"[Fix] {len(errs)} erreur(s) détectée(s)...")
    current_log  = build_log   # FIX: log mis à jour à chaque tentative
    current_errs = errs

    for attempt in range(1, max_attempts + 1):
        log(f"[Fix] Tentative {attempt}/{max_attempts}")

        # FIX: lire les fichiers en entier (8000 chars, pas 2500)
        curr = {}
        for p in gen_files:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp):
                with open(fp, "r") as f:
                    curr[p] = f.read()[:8000]  # FIX: 8000 au lieu de 2500

        ctx     = "".join(f"--- {p} ---\n{c}\n\n" for p, c in curr.items())
        err_str = "\n".join(current_errs[:10])

        # Différence avec la version originale pour aider l'IA
        diff_info = ""
        for p, orig in bak.items():
            new_content = curr.get(p, "")
            if new_content and orig != new_content:
                diff_info += f"\n[Modifié: {p}]\n"

        prompt = (
            BARE_METAL_RULES + "\n\n"
            "ERREURS DE COMPILATION:\n```\n" + err_str + "\n```\n\n"
            "LOG COMPLET (fin):\n```\n" + current_log[-2000:] + "\n```\n\n"  # FIX: plus de log
            "FICHIERS ACTUELS:\n" + ctx + "\n"
            "FICHIERS MODIFIÉS CE CYCLE:" + diff_info + "\n\n"
            "Instructions:\n"
            "- Corrige TOUTES les erreurs listées\n"
            "- Code complet, pas de '...'\n"
            "- Vérifie que TOUS les includes nécessaires sont là\n"
            "- Pour bare metal: ZERO stdint.h, utiliser 'unsigned int' à la place de uint32_t\n\n"
            "FORMAT:\n=== FILE: fichier.ext ===\n[code]\n=== END FILE ==="
        )

        resp = gemini(prompt, max_tokens=24576, timeout=90, context_tag=f"fix/{attempt}")
        if not resp:
            continue

        files, _ = parse_files(resp)
        if not files:
            log("[Fix] Rien parsé dans la réponse de fix", "WARN")
            continue

        write_files(files)
        ok, current_log, current_errs = make_build()  # FIX: met à jour current_log

        if ok:
            all_fixed = list(files.keys())
            git_push(
                "fix: corrections compilation",
                all_fixed,
                f"Auto-fix: {len(errs)} erreurs -> 0",
                model
            )
            d("🔧 Auto-fix OK",
              f"{len(errs)} erreur(s) corrigée(s) en {attempt} tentative(s).", 0x00AAFF)
            return True, {"attempts": attempt}

        log(f"[Fix] {len(current_errs)} erreur(s) restante(s) après tentative {attempt}", "WARN")
        time.sleep(10)

    restore_files(bak)
    return False, {"attempts": max_attempts}

# ══════════════════════════════════════════════════════════════════════════════
# GESTION DES PULL REQUESTS
# ══════════════════════════════════════════════════════════════════════════════

def analyze_pr_with_ai(pr_info, pr_files_data, pr_commits):
    """
    Analyse complète d'une PR avec l'IA.
    Retourne un dict avec review, inline_comments, décision.
    """
    num   = pr_info.get("number", "?")
    title = pr_info.get("title", "")
    body  = pr_info.get("body", "") or ""
    base  = pr_info.get("base", {}).get("ref", "main")
    head  = pr_info.get("head", {}).get("ref", "?")
    author= pr_info.get("user", {}).get("login", "?")

    # Liste des fichiers
    file_list = "\n".join([
        f"- {f.get('filename','?')} "
        f"(+{f.get('additions',0)} -{f.get('deletions',0)} ~{f.get('changes',0)})"
        for f in pr_files_data[:20]
    ])

    # Patches des 6 premiers fichiers .c/.h/.asm
    patches = ""
    code_files = [f for f in pr_files_data
                  if any(f.get("filename","").endswith(e) for e in [".c",".h",".asm",".ld"])]
    for f in code_files[:6]:
        fname = f.get("filename","")
        patch = f.get("patch","")[:1500]
        if patch:
            patches += f"\n{'='*40}\n{fname}:\n{patch}\n"

    # Résumé commits
    commit_msgs = "\n".join(
        f"- {c.get('commit',{}).get('message','')[:80]}"
        for c in (pr_commits or [])[:10]
    )

    prompt = (
        f"Tu es un expert OS bare metal x86 qui fait une code review de qualité.\n\n"
        + BARE_METAL_RULES + "\n\n"
        f"PULL REQUEST #{num}: {title}\n"
        f"Auteur: {author} | Base: {base} <- {head}\n"
        f"Description: {body[:600]}\n\n"
        f"FICHIERS ({len(pr_files_data)}):\n{file_list}\n\n"
        f"COMMITS:\n{commit_msgs}\n\n"
        f"CHANGEMENTS (extraits):\n{patches}\n\n"
        "Fais une review APPROFONDIE. Réponds en JSON:\n"
        "{\n"
        '  "decision": "APPROVE|REQUEST_CHANGES|COMMENT",\n'
        '  "summary": "Résumé en 2-3 phrases",\n'
        '  "problems": ["prob1", "prob2"],\n'
        '  "positives": ["point1", "point2"],\n'
        '  "inline_comments": [\n'
        '    {"path": "kernel/idt.c", "line": 42, "comment": "..."}\n'
        '  ],\n'
        '  "merge_safe": true|false,\n'
        '  "bare_metal_violations": ["violation1"]\n'
        "}"
    )

    resp = gemini(prompt, max_tokens=4096, timeout=60, context_tag=f"pr/{num}")
    if not resp:
        return None

    # Parser JSON
    clean = resp.strip()
    if clean.startswith("```"):
        lines = clean.split("\n")[1:]
        if lines and lines[-1].strip() == "```": lines = lines[:-1]
        clean = "\n".join(lines).strip()

    try:
        i = clean.find("{")
        j = clean.rfind("}") + 1
        if i >= 0 and j > i:
            return json.loads(clean[i:j])
    except json.JSONDecodeError as e:
        log(f"[PR] JSON parse error: {e}", "DEBUG")

    # Fallback: retourner le texte brut
    return {"decision": "COMMENT", "summary": resp[:500], "problems": [],
            "positives": [], "inline_comments": [], "merge_safe": False,
            "bare_metal_violations": []}

def format_pr_review_comment(num, analysis, model_used):
    """Formate le commentaire de review PR pour GitHub."""
    if not analysis:
        return f"## ❓ Review automatique — PR #{num}\n\nImpossible d'analyser cette PR.\n"

    decision       = analysis.get("decision", "COMMENT")
    summary        = analysis.get("summary", "")
    problems       = analysis.get("problems", [])
    positives      = analysis.get("positives", [])
    violations     = analysis.get("bare_metal_violations", [])
    merge_safe     = analysis.get("merge_safe", False)

    icon = {"APPROVE": "✅", "REQUEST_CHANGES": "🔴", "COMMENT": "💬"}.get(decision, "💬")
    color_emoji = "🟢" if merge_safe else "🔴"

    body = f"""## {icon} Review automatique MaxOS AI — PR #{num}

> **Décision**: `{decision}` | **Merge safe**: {color_emoji}

{summary}

"""
    if problems:
        body += "### ❌ Problèmes détectés\n"
        body += "\n".join(f"- {p}" for p in problems) + "\n\n"

    if positives:
        body += "### ✅ Points positifs\n"
        body += "\n".join(f"- {p}" for p in positives) + "\n\n"

    if violations:
        body += "### ⚠️ Violations bare metal\n"
        body += "\n".join(f"- `{v}`" for v in violations) + "\n\n"

    body += f"\n---\n*MaxOS AI Developer v{VERSION} | {model_used} | {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC*"
    return body

def handle_pull_requests():
    """Traite toutes les PRs ouvertes."""
    prs = gh_open_prs()
    if not prs:
        log("[PR] Aucune PR ouverte")
        return

    log(f"[PR] {len(prs)} PR(s) à traiter")
    gh_ensure_labels({k: v for k, v in STANDARD_LABELS.items()
                      if k in ("ai-reviewed","ai-approved","ai-rejected","needs-fix","kernel","driver","app")})

    bot_logins = {"MaxOS-AI-Bot", "github-actions[bot]", "dependabot[bot]"}

    for pr in prs[:5]:
        num    = pr.get("number")
        title  = pr.get("title", "")
        author = pr.get("user", {}).get("login", "")

        if author in bot_logins:
            continue

        log(f"[PR] #{num} '{title}' par {author}")

        # Vérifier si déjà reviewé par l'IA
        existing_reviews = gh_pr_reviews(num)
        already_reviewed = any(
            r.get("user", {}).get("login", "") in bot_logins
            for r in (existing_reviews or [])
        )
        if already_reviewed:
            log(f"[PR] #{num} déjà reviewé, skip")
            continue

        pr_info    = github_api("GET", f"pulls/{num}") or pr
        files_data = gh_pr_files(num)
        commits    = gh_pr_commits(num)

        # Analyse IA
        model = ACTIVE_MODELS.get(KEY_STATE["current_index"], {}).get("model", "?")
        analysis = analyze_pr_with_ai(pr_info, files_data, commits)

        # Poster la review
        comment_body = format_pr_review_comment(num, analysis, model)
        decision     = (analysis or {}).get("decision", "COMMENT")
        merge_safe   = (analysis or {}).get("merge_safe", False)
        inline_cmts  = (analysis or {}).get("inline_comments", [])

        # Post review avec commentaires inline
        if decision == "APPROVE" and merge_safe:
            gh_approve_pr(num, comment_body)
            gh_add_labels_to_issue(num, ["ai-approved", "ai-reviewed"])
        elif decision == "REQUEST_CHANGES":
            gh_request_changes(num, comment_body, inline_cmts if inline_cmts else None)
            gh_add_labels_to_issue(num, ["ai-rejected", "ai-reviewed", "needs-fix"])
        else:
            gh_post_pr_review(num, comment_body, "COMMENT",
                              inline_cmts if inline_cmts else None)
            gh_add_labels_to_issue(num, ["ai-reviewed"])

        # Labels de catégorie selon les fichiers
        cat_labels = []
        for f in files_data[:10]:
            fname = f.get("filename","")
            if "kernel/" in fname:   cat_labels.append("kernel")
            if "drivers/" in fname:  cat_labels.append("driver")
            if "apps/" in fname:     cat_labels.append("app")
        if cat_labels:
            gh_add_labels_to_issue(num, list(set(cat_labels)))

        d(f"📋 PR #{num} reviewée",
          f"**{title[:60]}**\nDécision: {decision} | Safe: {'✅' if merge_safe else '❌'}",
          0x00AAFF if decision == "APPROVE" else 0xFF4444 if decision == "REQUEST_CHANGES" else 0xFFA500,
          [{"name": "Auteur",   "value": author,   "inline": True},
           {"name": "Décision", "value": decision, "inline": True},
           {"name": "Fichiers", "value": str(len(files_data)), "inline": True}])

        log(f"[PR] #{num} -> {decision}")
        time.sleep(2)  # Eviter le spam GitHub

# ══════════════════════════════════════════════════════════════════════════════
# GESTION DES ISSUES — NOUVEAU v10
# ══════════════════════════════════════════════════════════════════════════════

def classify_issue_with_ai(issue):
    """
    Classe une issue et génère une réponse automatique.
    Retourne un dict avec classification, réponse, action.
    """
    num    = issue.get("number", "?")
    title  = issue.get("title", "")
    body   = issue.get("body", "") or ""
    author = issue.get("user", {}).get("login", "?")
    labels = [l.get("name","") for l in issue.get("labels", [])]

    prompt = (
        f"Tu es le bot de gestion d'issues du projet MaxOS, un OS bare metal x86.\n\n"
        + BARE_METAL_RULES + "\n\n"
        f"ISSUE #{num}: {title}\n"
        f"Auteur: {author}\n"
        f"Labels actuels: {', '.join(labels) if labels else 'aucun'}\n"
        f"Corps:\n{body[:1500]}\n\n"
        "Analyse cette issue et réponds en JSON:\n"
        "{\n"
        '  "type": "bug|enhancement|question|duplicate|wontfix|invalid",\n'
        '  "priority": "critical|high|medium|low",\n'
        '  "component": "kernel|driver|app|boot|docs|other",\n'
        '  "labels_to_add": ["bug", "kernel"],\n'
        '  "action": "respond|close|close_not_planned|reopen|label_only",\n'
        '  "close_reason": "completed|not_planned|null",\n'
        '  "response": "Réponse en français à poster sur l\'issue",\n'
        '  "is_duplicate": false,\n'
        '  "milestone_suggestion": "Kernel stable|null",\n'
        '  "assignee_suggestion": "null"\n'
        "}\n\n"
        "Pour les bugs valides: respond avec une réponse utile et labels appropriés.\n"
        "Pour les questions simples: respond avec la réponse.\n"
        "Pour les demandes hors-scope ou invalides: close_not_planned.\n"
        "Pour les doublons: label only avec 'duplicate'."
    )

    resp = gemini(prompt, max_tokens=2048, timeout=45, context_tag=f"issue/{num}")
    if not resp:
        return None

    clean = resp.strip()
    if clean.startswith("```"):
        lines = clean.split("\n")[1:]
        if lines and lines[-1].strip() == "```": lines = lines[:-1]
        clean = "\n".join(lines).strip()

    try:
        i = clean.find("{")
        j = clean.rfind("}") + 1
        if i >= 0 and j > i:
            return json.loads(clean[i:j])
    except json.JSONDecodeError:
        pass

    return None

def format_issue_response(num, analysis, model_used):
    """Formate la réponse à une issue."""
    if not analysis:
        return None

    response = analysis.get("response", "")
    itype    = analysis.get("type", "?")
    priority = analysis.get("priority", "?")
    comp     = analysis.get("component", "?")

    if not response:
        return None

    icon_map = {
        "bug":         "🐛",
        "enhancement": "✨",
        "question":    "❓",
        "duplicate":   "🔄",
        "wontfix":     "🚫",
        "invalid":     "❌",
    }
    icon = icon_map.get(itype, "💬")

    body = f"""{icon} **Réponse automatique MaxOS AI**

{response}

---
| Champ | Valeur |
|---|---|
| Type | `{itype}` |
| Priorité | `{priority}` |
| Composant | `{comp}` |

*MaxOS AI Developer v{VERSION} | {model_used} | {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC*"""

    return body

def handle_issues():
    """
    Traite les issues ouvertes:
    - Classifie avec l'IA
    - Poste une réponse
    - Assigne des labels
    - Ferme si nécessaire
    - Assigne un milestone
    """
    issues = gh_open_issues()
    if not issues:
        log("[Issues] Aucune issue ouverte")
        return

    log(f"[Issues] {len(issues)} issue(s) à traiter")

    # S'assurer que les labels standard existent
    gh_ensure_labels(STANDARD_LABELS)

    bot_logins = {"MaxOS-AI-Bot", "github-actions[bot]"}

    for issue in issues[:10]:  # Max 10 issues par run
        num    = issue.get("number")
        title  = issue.get("title", "")
        author = issue.get("user", {}).get("login", "")

        # Ignorer les issues créées par le bot
        if author in bot_logins:
            continue

        # Vérifier si déjà commentée par le bot
        timeline = gh_issue_timeline(num)
        already_handled = any(
            e.get("actor", {}).get("login", "") in bot_logins
            or e.get("user", {}).get("login", "") in bot_logins
            for e in (timeline or [])
        )
        if already_handled:
            log(f"[Issues] #{num} déjà traitée, skip")
            continue

        log(f"[Issues] #{num} '{title}' par {author}")

        model    = ACTIVE_MODELS.get(KEY_STATE["current_index"], {}).get("model", "?")
        analysis = classify_issue_with_ai(issue)

        if not analysis:
            log(f"[Issues] #{num} analyse IA échouée", "WARN")
            continue

        action     = analysis.get("action", "label_only")
        labels     = analysis.get("labels_to_add", [])
        close_reason = analysis.get("close_reason")
        milestone_s  = analysis.get("milestone_suggestion")

        # Appliquer les labels
        if labels:
            valid_labels = [l for l in labels if l in STANDARD_LABELS]
            if valid_labels:
                gh_add_labels_to_issue(num, valid_labels)

        # Poster la réponse si nécessaire
        if action in ("respond", "close", "close_not_planned"):
            comment = format_issue_response(num, analysis, model)
            if comment:
                gh_post_issue_comment(num, comment)

        # Assigner milestone si suggéré
        if milestone_s and milestone_s != "null":
            ms_num = gh_ensure_milestone(milestone_s)
            if ms_num:
                gh_assign_milestone(num, ms_num)

        # Action de fermeture
        if action == "close":
            gh_close_issue(num, "completed")
            log(f"[Issues] #{num} fermée (completed)")
        elif action == "close_not_planned":
            gh_close_issue(num, "not_planned")
            log(f"[Issues] #{num} fermée (not_planned)")

        itype = analysis.get("type", "?")
        d(f"🎫 Issue #{num} traitée",
          f"**{title[:60]}**",
          0x00FF88 if action in ("close",) else 0x5865F2,
          [{"name": "Auteur",  "value": author,  "inline": True},
           {"name": "Type",    "value": itype,   "inline": True},
           {"name": "Action",  "value": action,  "inline": True}])

        log(f"[Issues] #{num} -> {action} ({itype})")
        time.sleep(2)

# ══════════════════════════════════════════════════════════════════════════════
# STALE BOT — FERMETURE DES ISSUES INACTIVES
# ══════════════════════════════════════════════════════════════════════════════

def handle_stale_issues(days_stale=30, days_close=7):
    """
    Détecte et ferme les issues inactives.
    - Après days_stale jours sans activité: label 'stale' + avertissement
    - Après days_stale+days_close jours: fermeture automatique
    """
    issues = gh_open_issues()
    if not issues:
        return

    log(f"[Stale] Vérification de {len(issues)} issue(s)...")
    now       = time.time()
    stale_sec = days_stale * 86400
    close_sec = (days_stale + days_close) * 86400

    stale_count = 0
    closed_count = 0

    for issue in issues:
        num         = issue.get("number")
        updated_at  = issue.get("updated_at", "")
        labels      = [l.get("name","") for l in issue.get("labels", [])]
        is_stale    = "stale" in labels

        try:
            updated_ts = datetime.strptime(updated_at, "%Y-%m-%dT%H:%M:%SZ").timestamp()
        except (ValueError, TypeError):
            continue

        age = now - updated_ts

        if age >= close_sec and is_stale:
            # Fermer définitivement
            gh_post_issue_comment(
                num,
                "🤖 **MaxOS AI**: Cette issue a été fermée automatiquement car "
                f"elle est restée inactive pendant plus de {days_stale + days_close} jours.\n\n"
                "Si le problème persiste, n'hésitez pas à rouvrir ou créer une nouvelle issue."
            )
            gh_close_issue(num, "not_planned")
            log(f"[Stale] #{num} fermée (inactive {int(age/86400)}j)")
            closed_count += 1

        elif age >= stale_sec and not is_stale:
            # Marquer comme stale
            gh_add_labels_to_issue(num, ["stale"])
            gh_post_issue_comment(
                num,
                f"⏰ **MaxOS AI**: Cette issue semble inactive depuis {int(age/86400)} jours.\n\n"
                f"Elle sera automatiquement fermée dans **{days_close} jours** "
                "si aucune activité n'est détectée. "
                "Merci de commenter si elle est toujours d'actualité."
            )
            log(f"[Stale] #{num} marquée stale ({int(age/86400)}j)")
            stale_count += 1

    if stale_count + closed_count > 0:
        log(f"[Stale] {stale_count} marquées, {closed_count} fermées")
        d("⏰ Stale bot",
          f"{stale_count} issue(s) marquées stale, {closed_count} fermée(s).",
          0xAAAAAA)

# ══════════════════════════════════════════════════════════════════════════════
# CHANGELOG AUTOMATIQUE
# ══════════════════════════════════════════════════════════════════════════════

def generate_changelog(prev_tag, current_tag, tasks_done):
    """Génère un changelog entre deux tags."""
    # Récupérer les commits entre les deux tags
    compare = gh_compare(prev_tag, "HEAD")
    commits = compare.get("commits", [])

    changelog = f"## Changelog {prev_tag} → {current_tag}\n\n"

    # Grouper par type de commit
    groups = {
        "kernel": [],
        "driver": [],
        "feat":   [],
        "fix":    [],
        "other":  [],
    }

    for commit in commits[:30]:
        msg = commit.get("commit", {}).get("message", "").split("\n")[0]
        sha = commit.get("sha","")[:7]
        if not msg:
            continue
        entry = f"- `{sha}` {msg[:80]}"
        if msg.startswith("kernel:"):    groups["kernel"].append(entry)
        elif msg.startswith("driver:"):  groups["driver"].append(entry)
        elif msg.startswith("feat"):     groups["feat"].append(entry)
        elif msg.startswith("fix:"):     groups["fix"].append(entry)
        else:                            groups["other"].append(entry)

    labels = {
        "kernel": "🔧 Kernel",
        "driver": "💾 Drivers",
        "feat":   "✨ Features",
        "fix":    "🐛 Fixes",
        "other":  "📝 Autres",
    }

    for key, entries in groups.items():
        if entries:
            changelog += f"### {labels[key]}\n"
            changelog += "\n".join(entries) + "\n\n"

    if not any(groups.values()):
        changelog += "\n".join(
            f"- {t.get('nom','?')[:60]} (`{t.get('sha','?')}`)"
            for t in tasks_done
        )

    return changelog

# ══════════════════════════════════════════════════════════════════════════════
# CRÉATION DE RELEASE ENRICHIE
# ══════════════════════════════════════════════════════════════════════════════

def create_release(tasks_done, tasks_failed, analyse, stats):
    """Crée une release GitHub enrichie avec changelog et métriques."""
    releases = gh_list_releases(5)

    last_tag = "v0.0.0"
    for r in releases:
        tag = r.get("tag_name", "")
        if re.match(r"v\d+\.\d+\.\d+", tag):
            last_tag = tag
            break

    try:
        parts = last_tag.lstrip("v").split(".")
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    except (ValueError, IndexError):
        major, minor, patch = 0, 0, 0

    score = analyse.get("score_actuel", 30)
    if score >= 70:
        minor += 1; patch = 0
    else:
        patch += 1

    new_tag  = f"v{major}.{minor}.{patch}"
    niveau   = analyse.get("niveau_os", "?")
    ms       = analyse.get("prochaine_milestone", "?")
    features = analyse.get("fonctionnalites_presentes", [])

    feat_txt = "\n".join(f"- ✅ {f}" for f in features[:8]) or "- (Aucune)"

    # Tâches réussies
    changes = ""
    for t in tasks_done:
        nom   = t.get("nom", "?")[:60]
        sha   = t.get("sha", "?")
        model = t.get("model", "?")
        fx    = " (après fix)" if t.get("fix_count", 0) > 0 else ""
        changes += f"- ✅ {nom} [`{sha}`] ({model}){fx}\n"

    # Tâches échouées
    failed_txt = ""
    if tasks_failed:
        failed_txt = "\n".join(f"- ❌ {n}" for n in tasks_failed)

    # Métriques globales
    total_elapsed = round(time.time() - START_TIME, 0)
    total_tokens  = sum(KEY_STATE["tokens_used"].values())
    models_used   = ", ".join(sorted(set(
        ACTIVE_MODELS.get(i, {}).get("model", "?")
        for i in range(len(API_KEYS))
        if i in ACTIVE_MODELS
    )))

    # Changelog depuis la release précédente
    changelog = generate_changelog(last_tag, new_tag, tasks_done)

    # ── Assemblage propre des sections ──────────────────────────────────────
    changes_txt = changes or "- Maintenance\n"

    report_section = ""
    if failed_txt:
        report_section = f"\n## ⏭️ Reporté\n\n{failed_txt}\n"

    now = datetime.utcnow()

    body = (
        f"# MaxOS {new_tag}\n\n"
        f"> 🤖 MaxOS AI Developer v{VERSION} - Objectif: Windows 11\n\n"
        f"---\n\n## 📊 État\n\n"
        f"| | |\n|---|---|\n"
        f"| Score | **{score}/100** |\n"
        f"| Niveau | {niveau} |\n"
        f"| Fichiers | {stats.get('files', 0)} |\n"
        f"| Lignes | {stats.get('lines', 0)} |\n"
        f"| Milestone | {ms} |\n\n"
        f"## ✅ Changements\n\n{changes_txt}"
        f"{report_section}"
        f"\n## 🧩 Fonctionnalités\n\n{feat_txt}\n\n"
        f"{changelog}\n"
        f"---\n\n## 🚀 Tester MaxOS\n\n"
        f"### Linux/WSL\n```bash\n"
        f"sudo apt install qemu-system-x86\n"
        f"qemu-system-i386 -drive format=raw,file=os.img,if=floppy "
        f"-boot a -vga std -k fr -m 32 -no-reboot\n```\n\n"
        f"### Windows (QEMU)\n```\n"
        f"qemu-system-i386.exe -drive format=raw,file=os.img,if=floppy "
        f"-boot a -vga std -k fr -m 32\n```\n\n"
        f"### Compiler\n```bash\n"
        f"sudo apt install nasm gcc make gcc-multilib\n"
        f"git clone https://github.com/{REPO_OWNER}/{REPO_NAME}\n"
        f"cd {REPO_NAME} && make\n```\n\n"
        f"## ⌨️ Contrôles\n\n"
        f"| Touche | Action |\n|---|---|\n"
        f"| TAB | Changer d'app |\n| F1 | Bloc-Notes |\n"
        f"| F2 | Terminal |\n| F3 | Sysinfo |\n| F4 | À propos |\n\n"
        f"## ⚙️ Technique\n\n"
        f"| | |\n|---|---|\n"
        f"| Arch | x86 32-bit Protected Mode |\n"
        f"| CC | GCC -m32 -ffreestanding -nostdlib |\n"
        f"| ASM | NASM ELF32 |\n"
        f"| IA | {models_used} |\n"
        f"| Durée | {int(total_elapsed)}s |\n"
        f"| ~Tokens | {total_tokens} |\n\n"
        f"---\n*MaxOS AI v{VERSION} | {now.strftime('%Y-%m-%d %H:%M')} UTC*\n"
    )

    url = gh_create_release(
        new_tag,
        f"MaxOS {new_tag} | {niveau} | {now.strftime('%Y-%m-%d')}",
        body,
        pre=(score < 50)
    )

    if url:
        d("🚀 Release " + new_tag,
          f"Score: {score}/100 | {niveau}", 0x00FF88,
          [{"name": "Version",  "value": new_tag,           "inline": True},
           {"name": "Score",    "value": f"{score}/100",    "inline": True},
           {"name": "Release",  "value": f"[Voir]({url})",  "inline": False}])
        log(f"[Release] {new_tag} -> {url}")

    return url
# ══════════════════════════════════════════════════════════════════════════════
# RAPPORT FINAL DISCORD
# ══════════════════════════════════════════════════════════════════════════════

def send_final_report(success, total, tasks_done, tasks_failed, analyse, stats):
    """Rapport final ultra-détaillé sur Discord."""
    score  = analyse.get("score_actuel", 30)
    niveau = analyse.get("niveau_os", "?")
    pct    = int(success / total * 100) if total > 0 else 0
    color  = 0x00FF88 if pct >= 80 else 0xFFA500 if pct >= 50 else 0xFF4444

    total_elapsed = round(time.time() - START_TIME, 0)
    total_tokens  = sum(KEY_STATE["tokens_used"].values())
    total_calls   = sum(KEY_STATE["usage_count"].values())
    total_errors  = sum(KEY_STATE["errors"].values())

    # Métriques de qualité si disponibles
    sources = read_all()
    quality = analyze_code_quality(sources)

    tasks_done_str = "\n".join(
        f"✅ {t.get('nom','?')[:40]} ({t.get('elapsed',0):.0f}s)"
        for t in tasks_done
    ) or "Aucune"

    tasks_fail_str = "\n".join(
        f"❌ {n[:40]}" for n in tasks_failed
    ) or "Aucune"

    d(f"🏁 Cycle terminé — {success}/{total} tâches",
      f"```\n{pbar(pct)}\n```",
      color,
      [
          {"name": "✅ Succès",        "value": str(success),              "inline": True},
          {"name": "❌ Échecs",         "value": str(total-success),        "inline": True},
          {"name": "📈 Taux",           "value": f"{pct}%",                 "inline": True},
          {"name": "⏱️ Durée",          "value": f"{int(total_elapsed)}s",  "inline": True},
          {"name": "🔑 Appels API",     "value": str(total_calls),          "inline": True},
          {"name": "💬 ~Tokens",        "value": str(total_tokens),         "inline": True},
          {"name": "📊 Score qualité",  "value": f"{quality['score']}/100", "inline": True},
          {"name": "📁 Fichiers",       "value": str(stats.get("files",0)), "inline": True},
          {"name": "📝 Lignes",         "value": str(stats.get("lines",0)), "inline": True},
          {"name": "✅ Tâches réussies","value": tasks_done_str[:400],      "inline": False},
          {"name": "❌ Tâches échouées","value": tasks_fail_str[:200],      "inline": False},
          {"name": "🔑 État clés",      "value": key_status(),              "inline": False},
      ])

    # Rapport violations bare metal si des violations trouvées
    if quality["violations"]:
        viols_str = "\n".join(quality["violations"][:10])
        d("⚠️ Violations bare metal détectées",
          f"```\n{viols_str}\n```",
          0xFF6600)

# ══════════════════════════════════════════════════════════════════════════════
# WATCHDOG ANTI-BOUCLE INFINIE
# ══════════════════════════════════════════════════════════════════════════════

MAX_RUNTIME_SECONDS = 3300  # 55 minutes (sous la limite GitHub Actions de 60min)

def check_watchdog():
    """Vérifie que le script ne dépasse pas la limite de temps."""
    elapsed = time.time() - START_TIME
    if elapsed >= MAX_RUNTIME_SECONDS:
        log(f"[Watchdog] Limite de {MAX_RUNTIME_SECONDS}s atteinte ({elapsed:.0f}s). Arrêt.", "WARN")
        d("⏰ Watchdog", f"Arrêt après {int(elapsed)}s (limite {MAX_RUNTIME_SECONDS}s)", 0xFFA500)
        return False
    return True

# ══════════════════════════════════════════════════════════════════════════════
# NETTOYAGE DES ARTEFACTS OBSOLÈTES
# ══════════════════════════════════════════════════════════════════════════════

def cleanup_build_artifacts():
    """Supprime les fichiers .o et .img orphelins dans le répertoire build."""
    build_dir = os.path.join(REPO_PATH, "build")
    if not os.path.exists(build_dir):
        return
    cleaned = 0
    for fname in os.listdir(build_dir):
        if fname.endswith(".o") or fname.endswith(".img.old"):
            fp = os.path.join(build_dir, fname)
            try:
                os.remove(fp)
                cleaned += 1
            except OSError:
                pass
    if cleaned:
        log(f"[Cleanup] {cleaned} artefact(s) supprimé(s)")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 60)
    print(f"  MaxOS AI Developer v{VERSION}")
    print(f"  gemini-2.5-flash | GitHub API complète | Issues + PRs")
    print("=" * 60 + "\n")

    # Init modèles Gemini
    if not find_all_models():
        print("FATAL: Aucune clé Gemini opérationnelle")
        sys.exit(1)

    # Notification de démarrage
    d(f"🤖 MaxOS AI v{VERSION} démarré",
      f"{len(ACTIVE_MODELS)}/{len(API_KEYS)} clés actives",
      0x5865F2,
      [{"name": "Modèles",
        "value": "\n".join(
            f"Clé {i+1}: {ACTIVE_MODELS[i]['model']}"
            for i in sorted(ACTIVE_MODELS.keys())
        ) or "Aucun",
        "inline": False},
       {"name": "Repo",   "value": f"{REPO_OWNER}/{REPO_NAME}", "inline": True},
       {"name": "Debug",  "value": "ON" if DEBUG else "OFF",    "inline": True}])

    # ── Nettoyage initial ────────────────────────────────────────────────────
    cleanup_build_artifacts()

    # ── Labels standard ──────────────────────────────────────────────────────
    log("\n[Setup] Création des labels standard...")
    gh_ensure_labels(STANDARD_LABELS)

    # ── Gestion Issues ───────────────────────────────────────────────────────
    log("\n[Issues] Traitement des issues...")
    handle_issues()

    if not check_watchdog():
        sys.exit(0)

    # ── Stale bot ────────────────────────────────────────────────────────────
    log("\n[Stale] Vérification des issues inactives...")
    handle_stale_issues(days_stale=21, days_close=7)

    # ── Pull Requests ─────────────────────────────────────────────────────────
    log("\n[PRs] Traitement des pull requests...")
    handle_pull_requests()

    if not check_watchdog():
        sys.exit(0)

    # ── Sources ──────────────────────────────────────────────────────────────
    sources = read_all(force=True)
    context = build_context(sources)
    stats   = proj_stats(sources)
    log(f"[Sources] {stats['files']} fichiers, {stats['lines']} lignes, "
        f"{stats['chars']} chars")

    # Analyse qualité code
    quality = analyze_code_quality(sources)
    log(f"[Qualité] Score: {quality['score']}/100 | "
        f"{quality['violation_count']} violation(s) | "
        f"{quality['c_files']} fichiers C | "
        f"{quality['asm_files']} fichiers ASM")

    if quality["violations"]:
        log("[Qualité] Violations détectées:", "WARN")
        for v in quality["violations"][:5]:
            log(f"  {v}", "WARN")

    # Dépendances circulaires
    circles = detect_circular_deps(sources)
    if circles:
        log(f"[Qualité] {len(circles)} dépendance(s) circulaire(s):", "WARN")
        for c in circles:
            log(f"  {c}", "WARN")

    # ── Phase 1: Analyse ─────────────────────────────────────────────────────
    print("\n" + "="*60 + "\n PHASE 1: Analyse\n" + "="*60)
    analyse = phase_analyse(context, stats)
    if not analyse:
        d("❌ Analyse échouée", "Impossible.", 0xFF0000)
        sys.exit(1)

    score      = analyse.get("score_actuel", 30)
    niveau     = analyse.get("niveau_os", "?")
    plan       = analyse.get("plan_ameliorations", [])
    milestone  = analyse.get("prochaine_milestone", "?")
    features   = analyse.get("fonctionnalites_presentes", [])
    manquantes = analyse.get("fonctionnalites_manquantes_critiques", [])

    log(f"[Analyse] Score={score} | {niveau}")
    log(f"[Analyse] {len(plan)} tâche(s) | {milestone}")

    # Trier par priorité
    order = {"CRITIQUE": 0, "HAUTE": 1, "NORMALE": 2, "BASSE": 3}
    plan  = sorted(plan, key=lambda t: order.get(t.get("priorite","NORMALE"), 2))

    # Créer/assigner le milestone GitHub
    if milestone and milestone != "?":
        ms_num = gh_ensure_milestone(milestone)
        log(f"[Milestone] '{milestone}' = #{ms_num}")

    # Status Discord de l'analyse
    d(f"📊 Score {score}/100 — {niveau}",
      "```\n" + pbar(score) + "\n```",
      0x00AAFF if score>=60 else 0xFFA500 if score>=30 else 0xFF4444,
      [{"name": "✅ Présentes",
        "value": "\n".join(f"+ {f}" for f in features[:5]) or "?",
        "inline": True},
       {"name": "❌ Manquantes",
        "value": "\n".join(f"- {f}" for f in manquantes[:5]) or "?",
        "inline": True},
       {"name": "📋 Plan",
        "value": "\n".join(
            f"[{i+1}] [{t.get('priorite','?')}] {t.get('nom','?')[:40]}"
            for i, t in enumerate(plan[:6])
        ), "inline": False},
       {"name": "🎯 Milestone",   "value": milestone[:80],      "inline": False},
       {"name": "🔑 Clés",        "value": key_status(),        "inline": False},
       {"name": "🛡️ Qualité",     "value": f"{quality['score']}/100 ({quality['violation_count']} violations)", "inline": True},
       {"name": "⏱️ Uptime",      "value": uptime_str(),        "inline": True}])

    # ── Phase 2: Implémentation ──────────────────────────────────────────────
    print("\n" + "="*60 + "\n PHASE 2: Implémentation\n" + "="*60)

    total        = len(plan)
    success      = 0
    tasks_done   = []
    tasks_failed = []

    for i, task in enumerate(plan, 1):
        # Vérifier le watchdog
        if not check_watchdog():
            break

        nom      = task.get("nom", f"Tâche {i}")
        priorite = task.get("priorite", "NORMALE")
        cat      = task.get("categorie", "?")
        model    = ACTIVE_MODELS.get(KEY_STATE["current_index"], {}).get("model", "?")

        print("\n" + "="*60)
        print(f"[{i}/{total}] [{priorite}] {nom}")
        print("="*60)

        d(f"[{i}/{total}] {nom[:60]}",
          "```\n" + pbar(int((i-1)/total*100)) + "\n```\n" +
          task.get("description","")[:150] + "...",
          0xFFA500,
          [{"name": "Priorité", "value": priorite, "inline": True},
           {"name": "Cat",      "value": cat,      "inline": True},
           {"name": "Modèle",   "value": model,    "inline": True},
           {"name": "Rate limit","value": f"{GH_RATE['remaining']}", "inline": True}])

        sources = read_all()
        ok, written, deleted, metrics = phase_implement(task, sources)

        # Enregistrer les métriques
        TASK_METRICS.append(metrics)

        _, sha_raw, _ = git_cmd(["rev-parse", "HEAD"])
        sha = sha_raw.strip()[:7] if sha_raw.strip() else "?"

        if ok:
            success += 1
            tasks_done.append({
                "nom":       nom,
                "sha":       sha,
                "files":     written + deleted,
                "model":     model,
                "elapsed":   metrics.get("elapsed", 0),
                "fix_count": metrics.get("fix_count", 0),
            })

            # Commit status GitHub
            full_sha = get_current_sha()
            if full_sha:
                gh_create_commit_status(
                    full_sha, "success",
                    f"MaxOS AI: {nom[:60]} ✅",
                    "maxos-ai/implement"
                )

            d(f"✅ Succès: {nom[:50]}",
              f"Commit `{sha}`", 0x00FF88,
              [{"name": "📝 Écrits",
                "value": "\n".join(f"`{f}`" for f in written[:5]) or "Aucun",
                "inline": True},
               {"name": "🗑️ Supprimés",
                "value": "\n".join(f"`{f}`" for f in deleted) or "Aucun",
                "inline": True},
               {"name": "📊 Progress",
                "value": pbar(int(i/total*100)),
                "inline": False},
               {"name": "⏱️ Temps",
                "value": f"{metrics.get('elapsed',0):.0f}s",
                "inline": True}])
        else:
            tasks_failed.append(nom)

            # Commit status d'échec
            full_sha = get_current_sha()
            if full_sha:
                err_summary = "; ".join(metrics.get("errors", [])[:2])[:100]
                gh_create_commit_status(
                    full_sha, "failure",
                    f"MaxOS AI: {nom[:40]} ❌ — {err_summary}",
                    "maxos-ai/implement"
                )

            d(f"❌ Échec: {nom[:50]}",
              f"Code restauré. Raison: {metrics.get('result','?')}",
              0xFF6600,
              [{"name": "Erreurs",
                "value": "\n".join(metrics.get("errors", ["?"])[:3])[:300] or "?",
                "inline": False}])

        # Pause entre tâches
        if i < total:
            n_ok = sum(1 for ii in range(len(API_KEYS))
                       if API_KEYS[ii] and
                       time.time() >= KEY_STATE["cooldowns"].get(ii, 0))
            pause = 10 if n_ok >= 2 else 20
            log(f"[Pause] {pause}s...")
            time.sleep(pause)

    # ── Release ──────────────────────────────────────────────────────────────
    if success > 0:
        log("\n[Release] Création de la release...")
        sources = read_all(force=True)
        stats2  = proj_stats(sources)
        create_release(tasks_done, tasks_failed, analyse, stats2)

    # ── Rapport final ─────────────────────────────────────────────────────────
    sources_final = read_all(force=True)
    stats_final   = proj_stats(sources_final)
    send_final_report(success, total, tasks_done, tasks_failed, analyse, stats_final)

    # ── Résumé console ───────────────────────────────────────────────────────
    print("\n" + "="*60)
    print(f"[FIN] {success}/{total} tâches réussies | "
          f"Uptime: {uptime_str()} | "
          f"Rate limit: {GH_RATE['remaining']}")
    if tasks_done:
        print("✅ Succès:")
        for t in tasks_done:
            print(f"  - {t['nom'][:60]} ({t['elapsed']:.0f}s)")
    if tasks_failed:
        print("❌ Échecs:")
        for n in tasks_failed:
            print(f"  - {n[:60]}")

if __name__ == "__main__":
    main()
