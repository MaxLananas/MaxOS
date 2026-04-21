#!/usr/bin/env python3
"""MaxOS AI Developer v18.0"""

import os, sys, json, time, subprocess, re, hashlib, traceback, random, socket, atexit
import urllib.request, urllib.error, urllib.parse
from datetime import datetime, timezone
from collections import defaultdict, deque

VERSION     = "18.0"
DEBUG       = os.environ.get("MAXOS_DEBUG", "0") == "1"
START_TIME  = time.time()
MAX_RUNTIME = 3300

REPO_OWNER = os.environ.get("REPO_OWNER", "MaxLananas")
REPO_NAME  = os.environ.get("REPO_NAME",  "MaxOS")
REPO_PATH  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GH_TOKEN   = os.environ.get("GH_PAT", "") or os.environ.get("GITHUB_TOKEN", "")
DISCORD_WH = os.environ.get("DISCORD_WEBHOOK", "")
HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.json")
BLACKLIST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blacklist.json")

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]
OPENROUTER_MODELS = [
    "mistralai/devstral-small:free",
    "tngtech/deepseek-r1t-chimera:free",
    "deepseek/deepseek-chat-v3-0324:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemini-2.5-flash-preview-05-20",
]
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "moonshotai/kimi-k2-instruct",
]
MISTRAL_MODELS = [
    "mistral-small-latest",
    "mistral-medium-latest",
    "open-mixtral-8x7b",
]

PROVIDER_SPECIALIZATION = {
    "gemini":     ["analyse", "plan", "wiki", "issue", "review"],
    "openrouter": ["impl", "fix", "asm", "kernel"],
    "groq":       ["fix", "impl", "issue"],
    "mistral":    ["impl", "fix", "plan"],
}

GH_RATE      = {"remaining": 5000, "reset": 0}
SOURCE_CACHE = {"hash": None, "data": None}
TASK_METRICS = []
_DISC_BUF    = []
_DISC_LAST   = 0.0
_DISC_INTV   = 15
_CYCLE_STATS = defaultdict(int)

CANONICAL_SIGNATURES = {
    "screen_init":       "void screen_init(void)",
    "screen_clear":      "void screen_clear(void)",
    "screen_putchar":    "void screen_putchar(char c, unsigned char color)",
    "screen_write":      "void screen_write(const char *str, unsigned char color)",
    "screen_writeln":    "void screen_writeln(const char *str, unsigned char color)",
    "screen_set_color":  "void screen_set_color(unsigned char color)",
    "screen_get_row":    "int screen_get_row(void)",
    "screen_scroll":     "void screen_scroll(void)",
    "keyboard_init":     "void keyboard_init(void)",
    "keyboard_getchar":  "char keyboard_getchar(void)",
    "keyboard_handler":  "void keyboard_handler(void)",
    "idt_init":          "void idt_init(void)",
    "idt_set_gate":      "void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags)",
    "isr_handler":       "void isr_handler(unsigned int num, unsigned int err)",
    "irq_handler":       "void irq_handler(unsigned int num)",
    "timer_init":        "void timer_init(unsigned int hz)",
    "timer_get_ticks":   "unsigned int timer_get_ticks(void)",
    "timer_sleep":       "void timer_sleep(unsigned int ms)",
    "mem_init":          "void mem_init(unsigned int mem_size_kb)",
    "mem_alloc_page":    "void *mem_alloc_page(void)",
    "mem_free_page":     "void mem_free_page(void *addr)",
    "mem_used_pages":    "unsigned int mem_used_pages(void)",
    "heap_init":         "void heap_init(void *start, unsigned int size)",
    "heap_alloc":        "void *heap_alloc(unsigned int size)",
    "heap_free":         "void heap_free(void *ptr)",
    "kmain":             "void kmain(void)",
    "terminal_init":     "void terminal_init(void)",
    "terminal_run":      "void terminal_run(void)",
    "terminal_process":  "void terminal_process(const char *cmd)",
    "mouse_init":        "void mouse_init(void)",
    "mouse_handler":     "void mouse_handler(void)",
    "fault_handler":     "void fault_handler(unsigned int num, unsigned int err)",
    "paging_init":       "void paging_init(void)",
    "paging_map":        "void paging_map(unsigned int virt, unsigned int phys, unsigned int flags)",
}

KNOWN_FIXES = {
    "undefined reference to `isr": "isr.asm DOIT avoir global isr0..isr47 ET isr.o dans Makefile OBJS.",
    "undefined reference to `main'": "kernel_entry.asm appelle kmain pas main.",
    "undefined reference to `kernel_main'": "La fonction d'entrée s'appelle kmain dans kernel.c.",
    "conflicting types for 'fault_handler'": "fault_handler signature EXACTE: void fault_handler(unsigned int num, unsigned int err).",
    "conflicting types for 'screen_write'": "screen_write signature EXACTE: void screen_write(const char *str, unsigned char color).",
    "conflicting types for 'vga_putchar'": "vga_putchar signature doit correspondre à vga.h.",
    "screen.h: No such file or directory": "screen.h est dans drivers/. Utiliser #include \"drivers/screen.h\" ou corriger -I dans CFLAGS.",
    "No rule to make target": "Fichier .o référencé dans Makefile mais source absent. Retirer des OBJS ou créer le fichier.",
    "bad register name `%eip'": "En mode 32-bit pas de push eip. Retirer cette ligne.",
    "too many arguments to function 'fault_handler'": "fault_handler prend exactement 2 args: (unsigned int num, unsigned int err).",
    "too few arguments to function 'screen_write'": "screen_write prend 2 args: string ET couleur.",
    "unknown type name 'task_t'": "Inclure kernel/task.h avant d'utiliser task_t.",
    "undefined reference to `idt_set_gate'": "idt.c doit être compilé et dans Makefile OBJS.",
    "undefined reference to `screen_write'": "drivers/screen.c doit être dans Makefile SRCS_C.",
    "unsigned_char": "unsigned_char n'existe pas. Utiliser unsigned char avec un espace.",
    "v_put": "v_put n'est pas une fonction canonique. Utiliser screen_putchar ou screen_write.",
    "v_str": "v_str n'est pas une fonction canonique. Utiliser screen_write.",
    "kernel_main": "kernel_main n'existe pas. Utiliser kmain.",
    "symbol `kmain' not defined": (
        "boot.asm ne peut PAS appeler kmain par nom — kmain est dans le kernel C. "
        "boot.asm doit: 1) charger le kernel depuis le disque vers 0x1000, "
        "2) faire 'jmp 0x1000' ou 'jmp 0x0000:0x1000' — JAMAIS 'call kmain' ou 'extern kmain'. "
        "kernel_entry.asm appelle kmain, pas boot.asm."
    ),
}

def ts():
    return datetime.now(timezone.utc).strftime("%H:%M:%S")

def uptime():
    s = int(time.time() - START_TIME)
    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"

def remaining_time():
    return max(0, MAX_RUNTIME - (time.time() - START_TIME))

def pbar(pct, w=20):
    pct = max(0, min(100, pct))
    f = int(w * pct / 100)
    return "█" * f + "░" * (w - f) + f" {pct}%"

ICONS = {
    "INFO": "📋", "WARN": "⚠️ ", "ERROR": "❌", "OK": "✅",
    "BUILD": "🔨", "GIT": "📦", "TIME": "⏱️ ", "AI": "🤖", "STAT": "📊", "FIX": "🔧",
    "HIST": "📚", "WIKI": "📖", "QEMU": "💻",
}

def log(msg, level="INFO"):
    print(f"[{ts()}] {ICONS.get(level, '📋')} {msg}", flush=True)

def watchdog():
    elapsed = time.time() - START_TIME
    if elapsed >= MAX_RUNTIME:
        log(f"Watchdog: {int(elapsed)}s/{MAX_RUNTIME}s", "WARN")
        disc_now("⏰ Watchdog", f"Arrêt après **{uptime()}**", 0xFFA500)
        return False
    return True

def _find_keys(prefix):
    keys = []
    for suffix in [""] + [f"_{i}" for i in range(2, 12)]:
        v = os.environ.get(f"{prefix}{suffix}", "").strip()
        if len(v) >= 8:
            keys.append(v)
    return keys

def _make_provider(ptype, pid, key, model, url):
    return {
        "type": ptype, "id": pid, "key": key, "model": model, "url": url,
        "cooldown": 0.0, "errors": 0, "calls": 0, "tokens": 0,
        "dead": False, "last_ok": 0.0,
        "response_times": deque(maxlen=10),
        "consec_429": 0, "success_rate": 1.0,
        "key_prefix": key[:8],
        "specializations": PROVIDER_SPECIALIZATION.get(ptype, []),
        "task_success": defaultdict(int),
        "task_fail": defaultdict(int),
    }

def load_providers():
    pools = []
    gem_keys = _find_keys("GEMINI_API_KEY")
    log(f"  [load] GEMINI     : {len(gem_keys)} key(s) × {len(GEMINI_MODELS)} = {len(gem_keys)*len(GEMINI_MODELS)}")
    gem = []
    for i, key in enumerate(gem_keys, 1):
        for m in GEMINI_MODELS:
            base = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"
            slug = m.replace("gemini-", "").replace("-", "").replace(".", "")[:14]
            gem.append(_make_provider("gemini", f"gm{i}_{slug}", key, m, f"{base}?key={key}"))
    if gem:
        pools.append(gem)

    or_keys = _find_keys("OPENROUTER_KEY")
    log(f"  [load] OPENROUTER : {len(or_keys)} key(s) × {len(OPENROUTER_MODELS)} = {len(or_keys)*len(OPENROUTER_MODELS)}")
    orl = []
    for i, key in enumerate(or_keys, 1):
        for m in OPENROUTER_MODELS:
            short = m.split("/")[-1].replace(":free", "")[:16]
            orl.append(_make_provider("openrouter", f"or{i}_{short}", key, m,
                                      "https://openrouter.ai/api/v1/chat/completions"))
    if orl:
        pools.append(orl)

    groq_keys = _find_keys("GROQ_KEY")
    log(f"  [load] GROQ       : {len(groq_keys)} key(s) × {len(GROQ_MODELS)} = {len(groq_keys)*len(GROQ_MODELS)}")
    gro = []
    for i, key in enumerate(groq_keys, 1):
        for m in GROQ_MODELS:
            slug = m.replace("/", "_").replace("-", "_")[:16]
            gro.append(_make_provider("groq", f"gr{i}_{slug}", key, m,
                                      "https://api.groq.com/openai/v1/chat/completions"))
    if gro:
        pools.append(gro)

    mis_keys = _find_keys("MISTRAL_KEY")
    log(f"  [load] MISTRAL    : {len(mis_keys)} key(s) × {len(MISTRAL_MODELS)} = {len(mis_keys)*len(MISTRAL_MODELS)}")
    mis = []
    for i, key in enumerate(mis_keys, 1):
        for m in MISTRAL_MODELS:
            mis.append(_make_provider("mistral", f"ms{i}_{m[:16]}", key, m,
                                      "https://api.mistral.ai/v1/chat/completions"))
    if mis:
        pools.append(mis)

    result = []
    max_len = max((len(p) for p in pools), default=0)
    for i in range(max_len):
        for pool in pools:
            if i < len(pool):
                result.append(pool[i])
    return result

PROVIDERS = load_providers()

def alive():
    now = time.time()
    al = [p for p in PROVIDERS if not p["dead"] and now >= p["cooldown"]]
    al.sort(key=lambda p: (p["consec_429"] * 5 + p["errors"] * 2, -p["success_rate"]))
    return al

def alive_for(tag):
    now = time.time()
    al = [p for p in PROVIDERS if not p["dead"] and now >= p["cooldown"]]
    specialized = [p for p in al if tag in p.get("specializations", [])]
    if specialized:
        specialized.sort(key=lambda p: (p["consec_429"] * 5 + p["errors"] * 2, -p["success_rate"]))
        return specialized
    al.sort(key=lambda p: (p["consec_429"] * 5 + p["errors"] * 2, -p["success_rate"]))
    return al

def non_dead():
    return [p for p in PROVIDERS if not p["dead"]]

def avg_rt(p):
    rt = p.get("response_times", [])
    return sum(rt) / len(rt) if rt else 999.0

def prov_summary():
    now = time.time()
    by = defaultdict(lambda: [0, 0, 0])
    for p in PROVIDERS:
        t = p["type"]
        if p["dead"]:
            by[t][2] += 1
        elif now >= p["cooldown"]:
            by[t][0] += 1
        else:
            by[t][1] += 1
    parts = [f"**{t}**: 🟢{v[0]} 🟡{v[1]} 💀{v[2]}" for t, v in sorted(by.items())]
    return f"{len(alive())}/{len(non_dead())} dispo — " + " | ".join(parts)

def _propagate_key_dead(key_prefix):
    count = 0
    for p in PROVIDERS:
        if p["key_prefix"] == key_prefix and not p["dead"]:
            p["dead"] = True
            count += 1
    if count:
        log(f"Key {key_prefix}*** → {count} provider(s) tués", "ERROR")

def penalize(p, secs=None, dead=False):
    if dead:
        p["dead"] = True
        _CYCLE_STATS["providers_dead"] += 1
        log(f"Provider {p['id']} → MORT", "ERROR")
        return
    p["errors"] += 1
    p["consec_429"] += 1
    p["success_rate"] = max(0.0, p["success_rate"] - 0.15)
    if secs is None:
        secs = min(15 * (2 ** min(p["errors"] - 1, 4)) + random.uniform(0, 3), 180)
    p["cooldown"] = time.time() + secs
    log(f"Provider {p['id']} → cooldown {int(secs)}s (errs={p['errors']})", "WARN")

def reward(p, elapsed, tag=None):
    p["errors"] = max(0, p["errors"] - 1)
    p["consec_429"] = 0
    p["last_ok"] = time.time()
    p["success_rate"] = min(1.0, p["success_rate"] + 0.05)
    p["response_times"].append(elapsed)
    if tag:
        p["task_success"][tag] += 1
    _CYCLE_STATS["total_calls"] += 1

def pick(tag=None):
    al = alive_for(tag) if tag else alive()
    if al:
        chosen = al[0]
        if DEBUG:
            log(f"  pick → {chosen['id']} sr={chosen['success_rate']:.2f} tag={tag}")
        return chosen
    nd = non_dead()
    if not nd:
        log("FATAL: tous les providers sont morts", "ERROR")
        disc_now("💀 Mort totale", "Arrêt.", 0xFF0000)
        sys.exit(1)
    best = min(nd, key=lambda p: p["cooldown"])
    wait = min(max(best["cooldown"] - time.time() + 0.5, 0.5), 90)
    log(f"Tous en cooldown → attente {int(wait)}s → {best['id']}", "TIME")
    _CYCLE_STATS["total_waits"] += 1
    time.sleep(wait)
    return best

def _call_gemini(p, prompt, max_tok, timeout):
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tok, "temperature": 0.05, "candidateCount": 1},
    }).encode("utf-8")
    req = urllib.request.Request(p["url"], data=payload,
                                  headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode("utf-8"))
    cands = data.get("candidates", [])
    if not cands:
        return None
    c = cands[0]
    if c.get("finishReason", "") in ("SAFETY", "RECITATION", "PROHIBITED_CONTENT"):
        return None
    parts = c.get("content", {}).get("parts", [])
    texts = [pt.get("text", "") for pt in parts
             if isinstance(pt, dict) and not pt.get("thought") and pt.get("text")]
    result = "".join(texts).strip()
    return result if result else None

def _call_compat(p, prompt, max_tok, timeout):
    limits = {"groq": 26000, "openrouter": 45000, "mistral": 50000}
    lim = limits.get(p["type"], 50000)
    if len(prompt) > lim:
        prompt = prompt[:lim] + "\n[TRONQUÉ]"
    if p["type"] == "groq":
        max_tok = min(max_tok, 8000)
    payload = json.dumps({
        "model": p["model"],
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tok, "temperature": 0.05,
    }).encode("utf-8")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {p['key']}"}
    if p["type"] == "openrouter":
        headers["HTTP-Referer"] = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
        headers["X-Title"] = f"MaxOS AI v{VERSION}"
    req = urllib.request.Request(p["url"], data=payload, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode("utf-8"))
    if "error" in data:
        raise RuntimeError(data["error"].get("message", "unknown")[:250])
    choices = data.get("choices", [])
    if not choices:
        return None
    content = choices[0].get("message", {}).get("content", "")
    return content.strip() if content else None

def ai_call(prompt, max_tokens=32768, timeout=160, tag="?"):
    if len(prompt) > 54000:
        prompt = prompt[:54000] + "\n[TRONQUÉ]"
    max_att = min(len(PROVIDERS) * 2, 30)
    last_error = "aucune tentative"
    _CYCLE_STATS["ai_calls"] += 1
    task_category = tag.split("/")[0] if "/" in tag else tag

    for attempt in range(1, max_att + 1):
        if not watchdog():
            return None
        p = pick(task_category)
        t0 = time.time()
        log(f"[{tag}] {p['type']}/{p['id']} att={attempt} sr={p['success_rate']:.2f}", "AI")
        try:
            text = (_call_gemini(p, prompt, max_tokens, timeout)
                    if p["type"] == "gemini"
                    else _call_compat(p, prompt, max_tokens, timeout))
            elapsed = round(time.time() - t0, 1)
            if not text or not text.strip():
                log(f"[{tag}] Réponse vide ({p['id']}) {elapsed}s", "WARN")
                penalize(p, 12)
                continue
            p["calls"] += 1
            p["tokens"] += len(text) // 4
            reward(p, elapsed, task_category)
            _CYCLE_STATS["total_tokens"] += len(text) // 4
            log(f"[{tag}] ✅ {len(text):,}c {elapsed}s ({p['type']}/{p['model'][:22]})", "OK")
            return text

        except urllib.error.HTTPError as e:
            elapsed = round(time.time() - t0, 1)
            body = ""
            try:
                body = e.read().decode("utf-8", errors="replace")[:600]
            except:
                pass
            last_error = f"HTTP {e.code}"
            log(f"[{tag}] HTTP {e.code} ({p['id']}) {elapsed}s", "WARN")
            p["task_fail"][task_category] += 1
            if e.code == 429:
                _CYCLE_STATS["total_429"] += 1
                penalize(p)
            elif e.code == 401:
                _propagate_key_dead(p["key_prefix"])
            elif e.code == 403:
                bl = body.lower()
                kill = ["denied", "banned", "suspended", "not authorized", "forbidden", "deactivated", "invalid api key"]
                if any(w in bl for w in kill):
                    _propagate_key_dead(p["key_prefix"])
                else:
                    penalize(p, 180)
            elif e.code == 404:
                penalize(p, dead=True)
            elif e.code == 400:
                if "not a valid model" in body.lower() or "no endpoints found" in body.lower():
                    penalize(p, dead=True)
                else:
                    penalize(p, 40)
            elif e.code in (500, 502, 503, 504):
                penalize(p, 20)
                time.sleep(2)
            elif e.code == 408:
                penalize(p, 25)
            else:
                penalize(p, 15)
                time.sleep(1)

        except (TimeoutError, socket.timeout):
            log(f"[{tag}] TIMEOUT {timeout}s ({p['id']})", "WARN")
            p["task_fail"][task_category] += 1
            penalize(p, 30)
        except urllib.error.URLError as e:
            log(f"[{tag}] URLError ({p['id']}): {e.reason}", "WARN")
            p["task_fail"][task_category] += 1
            penalize(p, 18)
            time.sleep(2)
        except RuntimeError as e:
            log(f"[{tag}] RuntimeError ({p['id']}): {e}", "WARN")
            p["task_fail"][task_category] += 1
            penalize(p, 22)
        except json.JSONDecodeError as e:
            log(f"[{tag}] JSON error ({p['id']}): {e}", "WARN")
            p["task_fail"][task_category] += 1
            penalize(p, 10)
        except Exception as e:
            log(f"[{tag}] Exception ({p['id']}): {type(e).__name__}: {e}", "ERROR")
            if DEBUG:
                traceback.print_exc()
            p["task_fail"][task_category] += 1
            penalize(p, 12)
            time.sleep(1)

    _CYCLE_STATS["ai_failures"] += 1
    log(f"[{tag}] ÉCHEC TOTAL {max_att} att. Dernière: {last_error}", "ERROR")
    return None

def _disc_raw(embeds):
    if not DISCORD_WH:
        return False
    payload = json.dumps({"username": f"MaxOS AI v{VERSION}", "embeds": embeds[:10]}).encode()
    req = urllib.request.Request(DISCORD_WH, data=payload,
                                  headers={"Content-Type": "application/json",
                                           "User-Agent": f"MaxOS-Bot/{VERSION}"},
                                  method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status in (200, 204)
    except Exception as ex:
        if DEBUG:
            log(f"Discord err: {ex}", "WARN")
        return False

def _make_embed(title, desc, color, fields=None):
    al = len(alive())
    nd = len(non_dead())
    tk = sum(p["tokens"] for p in PROVIDERS)
    ca = sum(p["calls"] for p in PROVIDERS)
    cur = alive()[0]["model"][:22] if alive() else "aucun"
    e = {
        "title": str(title)[:256],
        "description": str(desc)[:4096],
        "color": color,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "footer": {"text": f"v{VERSION} | {cur} | {al}/{nd} | up {uptime()} | ~{tk:,}tk | {ca}c"},
    }
    if fields:
        e["fields"] = [
            {"name": str(f.get("name", "?"))[:256],
             "value": str(f.get("value", "?"))[:1024],
             "inline": bool(f.get("inline", False))}
            for f in fields[:25]
            if f.get("value") and str(f.get("value", "")).strip()
        ]
    return e

def disc_log(title, desc="", color=0x5865F2):
    _DISC_BUF.append((title, desc, color))
    _flush_disc(False)

def _flush_disc(force=True):
    global _DISC_LAST
    now = time.time()
    if not force and now - _DISC_LAST < _DISC_INTV:
        return
    while len(_DISC_BUF) > 50:
        _DISC_BUF.pop(0)
    if not _DISC_BUF:
        return
    embeds = []
    while _DISC_BUF and len(embeds) < 10:
        t, d, c = _DISC_BUF.pop(0)
        embeds.append(_make_embed(t, d, c))
    if embeds:
        _disc_raw(embeds)
        _DISC_LAST = time.time()

def disc_now(title, desc="", color=0x5865F2, fields=None):
    _flush_disc(True)
    _disc_raw([_make_embed(title, desc, color, fields)])

atexit.register(_flush_disc, True)

def _load_history():
    if not os.path.exists(HISTORY_FILE):
        return {"cycles": [], "task_outcomes": {}, "known_errors": {}, "score_history": [], "cycle_count": 0}
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {"cycles": [], "task_outcomes": {}, "known_errors": {}, "score_history": [], "cycle_count": 0}

def _save_history(history):
    try:
        if len(history.get("cycles", [])) > 20:
            history["cycles"] = history["cycles"][-20:]
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        log(f"History save error: {e}", "WARN")

def _load_blacklist():
    if not os.path.exists(BLACKLIST_FILE):
        return {}
    try:
        with open(BLACKLIST_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def _save_blacklist(bl):
    try:
        with open(BLACKLIST_FILE, "w") as f:
            json.dump(bl, f, indent=2)
    except:
        pass

def _history_summary(history):
    cycles = history.get("cycles", [])
    if not cycles:
        return "Aucun historique disponible."
    last = cycles[-1] if cycles else {}
    scores = history.get("score_history", [])
    trend = "stable"
    if len(scores) >= 3:
        if scores[-1] > scores[-3]:
            trend = "↗️ en hausse"
        elif scores[-1] < scores[-3]:
            trend = "↘️ en baisse"
    recent_fails = []
    for task_name, outcomes in history.get("task_outcomes", {}).items():
        fails = outcomes.get("fail", 0)
        total = outcomes.get("success", 0) + fails
        if total > 0 and fails / total > 0.6:
            recent_fails.append(f"{task_name[:40]} ({fails}/{total} échecs)")
    summary = f"Cycles: {history.get('cycle_count', 0)} | Score trend: {trend}"
    if scores:
        summary += f" | Dernier score: {scores[-1]}/100"
    if recent_fails:
        summary += f"\nTâches difficiles: {', '.join(recent_fails[:3])}"
    return summary

def _update_history(history, cycle_data):
    history["cycle_count"] = history.get("cycle_count", 0) + 1
    compact = {
        "ts": int(time.time()),
        "score": cycle_data.get("score", 0),
        "success": cycle_data.get("success", 0),
        "total": cycle_data.get("total", 0),
        "img_ok": cycle_data.get("img_ok", False),
        "tasks_done": [t.get("nom", "?")[:30] for t in cycle_data.get("tasks_done", [])],
        "tasks_failed": [n[:30] for n in cycle_data.get("tasks_failed", [])],
    }
    history.setdefault("cycles", []).append(compact)
    history.setdefault("score_history", []).append(cycle_data.get("score", 0))
    if len(history["score_history"]) > 50:
        history["score_history"] = history["score_history"][-50:]
    for t in cycle_data.get("tasks_done", []):
        name = t.get("nom", "?")
        history.setdefault("task_outcomes", {}).setdefault(name, {"success": 0, "fail": 0})
        history["task_outcomes"][name]["success"] += 1
    for name in cycle_data.get("tasks_failed", []):
        history.setdefault("task_outcomes", {}).setdefault(name, {"success": 0, "fail": 0})
        history["task_outcomes"][name]["fail"] += 1
    return history

def _check_blacklist(blacklist, task_name):
    entry = blacklist.get(task_name, {})
    fails = entry.get("consecutive_fails", 0)
    if fails >= 3:
        last_fail = entry.get("last_fail", 0)
        if time.time() - last_fail < 86400 * 2:
            return True
    return False

def _update_blacklist(blacklist, task_name, success):
    entry = blacklist.setdefault(task_name, {"consecutive_fails": 0, "last_fail": 0})
    if success:
        entry["consecutive_fails"] = 0
    else:
        entry["consecutive_fails"] = entry.get("consecutive_fails", 0) + 1
        entry["last_fail"] = int(time.time())
    return blacklist

def gh_api(method, endpoint, data=None, raw_url=None, retry=3, silent=False):
    if not GH_TOKEN:
        return None
    url = raw_url or f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/{endpoint}"
    payload = json.dumps(data).encode() if data else None
    for att in range(1, retry + 1):
        req = urllib.request.Request(url, data=payload, headers={
            "Authorization": f"Bearer {GH_TOKEN}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": f"MaxOS-AI/{VERSION}",
            "X-GitHub-Api-Version": "2022-11-28",
        }, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                rem = r.headers.get("X-RateLimit-Remaining")
                rst = r.headers.get("X-RateLimit-Reset")
                if rem:
                    GH_RATE["remaining"] = int(rem)
                if rst:
                    GH_RATE["reset"] = int(rst)
                if GH_RATE["remaining"] < 80:
                    log(f"GH rate limit: {GH_RATE['remaining']} restants!", "WARN")
                raw = r.read().decode("utf-8", errors="replace")
                return json.loads(raw) if raw.strip() else {}
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", errors="replace")[:400]
            except:
                pass
            if e.code == 403 and "rate limit" in body.lower():
                wait = max(GH_RATE["reset"] - time.time() + 5, 60)
                log(f"GH rate limit → attente {int(wait)}s", "WARN")
                time.sleep(wait)
                continue
            if e.code in (500, 502, 503, 504) and att < retry:
                time.sleep(5 * att)
                continue
            if not silent:
                log(f"GH {method} {endpoint[:60]} HTTP {e.code}: {body[:120]}", "WARN")
            return None
        except Exception as ex:
            if att < retry:
                time.sleep(3)
                continue
            if not silent:
                log(f"GH ex: {ex}", "ERROR")
            return None
    return None

def gh_open_prs():
    r = gh_api("GET", "pulls?state=open&per_page=20&sort=updated&direction=desc")
    return r if isinstance(r, list) else []

def gh_pr_files(n):
    r = gh_api("GET", f"pulls/{n}/files?per_page=50")
    return r if isinstance(r, list) else []

def gh_pr_reviews(n):
    r = gh_api("GET", f"pulls/{n}/reviews")
    return r if isinstance(r, list) else []

def gh_post_review(n, body, event="COMMENT", comments=None):
    pay = {"body": body, "event": event}
    if comments:
        pay["comments"] = [
            {"path": c["path"], "line": c.get("line", 1), "side": "RIGHT", "body": c["body"]}
            for c in comments if c.get("path") and c.get("body")
        ]
    return gh_api("POST", f"pulls/{n}/reviews", pay)

def gh_approve_pr(n, body):
    return gh_post_review(n, body, "APPROVE")

def gh_req_changes(n, body, comments=None):
    return gh_post_review(n, body, "REQUEST_CHANGES", comments)

def gh_open_issues():
    r = gh_api("GET", "issues?state=open&per_page=30&sort=updated&direction=desc")
    if not isinstance(r, list):
        return []
    return [i for i in r if not i.get("pull_request")]

def gh_issue_comments(n):
    r = gh_api("GET", f"issues/{n}/comments?per_page=50")
    return r if isinstance(r, list) else []

def gh_close_issue(n, reason="completed"):
    gh_api("PATCH", f"issues/{n}", {"state": "closed", "state_reason": reason})

def gh_add_labels(n, labels):
    if labels:
        gh_api("POST", f"issues/{n}/labels", {"labels": labels})

def gh_post_comment(n, body):
    gh_api("POST", f"issues/{n}/comments", {"body": body})

def gh_create_issue(title, body, labels=None):
    pay = {"title": title, "body": body}
    if labels:
        pay["labels"] = labels
    return gh_api("POST", "issues", pay)

def gh_list_labels():
    r = gh_api("GET", "labels?per_page=100")
    return {l["name"]: l for l in (r if isinstance(r, list) else [])}

def gh_ensure_labels(desired):
    ex = gh_list_labels()
    created = 0
    for name, color in desired.items():
        if name not in ex:
            gh_api("POST", "labels", {"name": name, "color": color, "description": f"[MaxOS AI] {name}"})
            created += 1
    if created:
        log(f"Labels: {created} créé(s)")

STANDARD_LABELS = {
    "ai-reviewed": "0075ca", "ai-approved": "0e8a16", "ai-rejected": "b60205",
    "ai-generated": "8b5cf6", "needs-fix": "e4e669", "bug": "d73a4a",
    "enhancement": "a2eeef", "stale": "eeeeee", "kernel": "5319e7",
    "driver": "1d76db", "app": "0052cc", "boot": "e11d48", "security": "b91c1c",
    "documentation": "0075ca", "qemu": "f9d0c4",
}

def gh_ensure_milestone(title, description=""):
    r = gh_api("GET", "milestones?state=open&per_page=30")
    for m in (r if isinstance(r, list) else []):
        if m.get("title") == title:
            return m.get("number")
    r2 = gh_api("POST", "milestones", {"title": title, "description": description or f"[AI] {title}"})
    return r2.get("number") if r2 else None

def gh_list_releases(n=10):
    r = gh_api("GET", f"releases?per_page={n}")
    return r if isinstance(r, list) else []

def gh_create_release(tag, name, body, pre=False):
    r = gh_api("POST", "releases", {
        "tag_name": tag, "target_commitish": "main",
        "name": name, "body": body, "draft": False, "prerelease": pre,
    })
    return r if r else None

def gh_upload_asset(release_id, filepath, name):
    if not GH_TOKEN or not os.path.exists(filepath):
        return None
    url = (f"https://uploads.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
           f"/releases/{release_id}/assets?name={name}")
    size = os.path.getsize(filepath)
    log(f"Upload asset: {name} ({size} bytes) → release {release_id}")
    try:
        with open(filepath, "rb") as f:
            data = f.read()
        req = urllib.request.Request(url, data=data, headers={
            "Authorization": f"Bearer {GH_TOKEN}",
            "Content-Type": "application/octet-stream",
            "User-Agent": f"MaxOS-AI/{VERSION}",
        }, method="POST")
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read().decode("utf-8", errors="replace"))
            url_dl = resp.get("browser_download_url", "?")
            log(f"Asset uploadé: {url_dl}", "OK")
            return url_dl
    except Exception as ex:
        log(f"Upload asset erreur: {ex}", "ERROR")
        return None

def gh_compare(base, head):
    r = gh_api("GET", f"compare/{base}...{head}")
    return r if isinstance(r, dict) else {}

def gh_get_wiki_page(title):
    slug = title.lower().replace(" ", "-")
    r = gh_api("GET", f"contents/docs/{slug}.md", silent=True)
    if r and isinstance(r, dict) and r.get("content"):
        import base64
        try:
            return base64.b64decode(r["content"]).decode("utf-8")
        except:
            return None
    return None

def gh_upsert_wiki_page(title, content):
    slug = title.lower().replace(" ", "-").replace("/", "-")
    path = f"docs/{slug}.md"
    existing = gh_api("GET", f"contents/{path}", silent=True)
    sha = existing.get("sha") if isinstance(existing, dict) else None
    import base64
    encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    pay = {
        "message": f"docs: update {title} [skip ci]",
        "content": encoded,
        "branch": "main",
    }
    if sha:
        pay["sha"] = sha
    result = gh_api("PUT", f"contents/{path}", pay)
    return result is not None

def git_cmd(args, timeout=60):
    try:
        r = subprocess.run(["git"] + args, cwd=REPO_PATH,
                           capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return False, "", f"timeout {timeout}s"
    except Exception as e:
        return False, "", str(e)

def git_sha(short=True):
    ok, out, _ = git_cmd(["rev-parse", "HEAD"])
    if not ok:
        return ""
    s = out.strip()
    return s[:7] if short else s

def git_current_branch():
    ok, out, _ = git_cmd(["branch", "--show-current"])
    return out.strip() if ok else "main"

def git_push(task_name, files, desc, model):
    if not files:
        return True, None, None
    dirs = set(f.split("/")[0] for f in files if "/" in f)
    pmap = {"kernel": "kernel", "drivers": "driver", "boot": "boot", "ui": "ui", "apps": "feat", "docs": "docs"}
    prefix = next((pmap[d] for d in pmap if d in dirs), "feat")
    fshort = ", ".join(os.path.basename(f) for f in files[:3])
    if len(files) > 3:
        fshort += f" +{len(files) - 3}"
    short = f"{prefix}: {task_name[:50]} [{fshort}]"
    body = (f"{short}\n\nFiles: {', '.join(files[:10])}\n"
            f"Model: {model}\nArch: x86-32 bare metal\n\n[skip ci]")
    git_cmd(["add", "-A"])
    ok, out, err = git_cmd(["commit", "-m", body])
    if not ok:
        if "nothing to commit" in (out + err):
            log("Git: rien à committer")
            return True, None, None
        log(f"Commit KO: {err[:250]}", "ERROR")
        return False, None, None
    sha = git_sha()
    ok2, _, e2 = git_cmd(["push", "--set-upstream", "origin", git_current_branch()])
    if not ok2:
        git_cmd(["pull", "--rebase", "--autostash"])
        ok2, _, e2 = git_cmd(["push"])
        if not ok2:
            log(f"Push KO: {e2[:250]}", "ERROR")
            return False, None, None
    _CYCLE_STATS["total_commits"] += 1
    log(f"Push OK: {sha} — {short[:60]}", "GIT")
    return True, sha, short

_ERR_RE = re.compile(
    r"(?:error:|fatal error:|fatal:|undefined reference|cannot find|no such file"
    r"|\*\*\* \[|nasm:.*error|ld:.*error|collect2: error|linker command failed"
    r"|multiple definition|duplicate symbol|identifier expected|undefined symbol)",
    re.IGNORECASE
)

def parse_errs(log_text):
    seen, result = [], []
    for line in log_text.split("\n"):
        s = line.strip()
        if s and _ERR_RE.search(s) and s not in seen:
            seen.append(s)
            result.append(s[:140])
    return result[:35]

def _detect_silent_fail(log_text, returncode):
    if returncode == 0:
        return None
    lines = log_text.split("\n")
    for line in lines:
        s = line.strip()
        if re.search(r"Error \d+", s) or "FAILED" in s:
            return s[:140]
        if "make[" in s and "Error" in s:
            return s[:140]
        if "*** " in s:
            return s[:140]
    non_empty = [l.strip() for l in lines if l.strip()]
    if non_empty:
        return f"Build fail silencieux. Dernières: {' | '.join(non_empty[-3:])}"
    return "Build fail sans sortie"

def make_build():
    subprocess.run(["make", "clean"], cwd=REPO_PATH, capture_output=True, timeout=30)
    build_dir = os.path.join(REPO_PATH, "build")
    os.makedirs(build_dir, exist_ok=True)
    t0 = time.time()
    try:
        r = subprocess.run(["make", "-j2"], cwd=REPO_PATH,
                           capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        log("Build TIMEOUT 180s", "ERROR")
        return False, "TIMEOUT", ["Build timeout après 180s"]

    el = round(time.time() - t0, 1)
    lt = r.stdout + r.stderr
    errs = parse_errs(lt)

    if r.returncode == 0:
        img_path = os.path.join(REPO_PATH, "os.img")
        if not os.path.exists(img_path):
            log("make OK mais os.img absent — création manuelle", "WARN")
            boot_bin = os.path.join(build_dir, "boot.bin")
            kernel_bin = os.path.join(build_dir, "kernel.bin")
            if os.path.exists(boot_bin):
                _create_osimg(boot_bin, kernel_bin if os.path.exists(kernel_bin) else None)
        _CYCLE_STATS["builds_ok"] += 1
        log(f"Build OK {el}s", "BUILD")
        disc_log("🔨 Build ✅", f"`{el}s`", 0x00CC44)
        return True, lt, []

    if not errs:
        silent_desc = _detect_silent_fail(lt, r.returncode)
        errs = [silent_desc] if silent_desc else [f"make rc={r.returncode} sans erreur parsable"]

    log(f"Build FAIL ({len(errs)} err) {el}s", "BUILD")
    for e in errs[:6]:
        log(f"  >> {e[:115]}", "BUILD")
    _CYCLE_STATS["builds_fail"] += 1
    es = "\n".join(f"`{e[:85]}`" for e in errs[:5])
    disc_log(f"🔨 Build ❌ ({len(errs)} err)", f"`{el}s`\n{es}", 0xFF2200)
    return False, lt, errs

def _create_osimg(boot_bin, kernel_bin=None):
    img_path = os.path.join(REPO_PATH, "os.img")
    try:
        subprocess.run(["dd", "if=/dev/zero", "of=" + img_path, "bs=512", "count=2880"],
                       cwd=REPO_PATH, capture_output=True, timeout=10)
        subprocess.run(["dd", "if=" + boot_bin, "of=" + img_path, "conv=notrunc"],
                       cwd=REPO_PATH, capture_output=True, timeout=10)
        if kernel_bin:
            subprocess.run(["dd", "if=" + kernel_bin, "of=" + img_path, "seek=1", "conv=notrunc"],
                           cwd=REPO_PATH, capture_output=True, timeout=10)
        size = os.path.getsize(img_path)
        log(f"os.img créé manuellement: {size} bytes", "OK")
        return True
    except Exception as e:
        log(f"Erreur création os.img: {e}", "ERROR")
        return False

def ensure_osimg():
    img_path = os.path.join(REPO_PATH, "os.img")
    build_dir = os.path.join(REPO_PATH, "build")
    boot_bin = os.path.join(build_dir, "boot.bin")
    kernel_bin = os.path.join(build_dir, "kernel.bin")
    if os.path.exists(img_path) and os.path.getsize(img_path) > 512:
        return True
    if os.path.exists(boot_bin):
        return _create_osimg(boot_bin, kernel_bin if os.path.exists(kernel_bin) else None)
    log("os.img et boot.bin absents — impossible de créer l'image", "WARN")
    return False

def validate_boot_sector():
    img_path = os.path.join(REPO_PATH, "os.img")
    if not os.path.exists(img_path):
        return False, "os.img absent"
    try:
        with open(img_path, "rb") as f:
            sector = f.read(512)
        if len(sector) < 512:
            return False, f"os.img trop petit: {len(sector)} bytes"
        if sector[510:512] == b'\x55\xAA':
            size = os.path.getsize(img_path)
            return True, f"Signature 0xAA55 ✅ | {size} bytes"
        else:
            sig = sector[510:512].hex()
            return False, f"Signature invalide: 0x{sig} (attendu 0xAA55)"
    except Exception as e:
        return False, f"Erreur lecture: {e}"

def run_qemu_test():
    img_path = os.path.join(REPO_PATH, "os.img")
    if not os.path.exists(img_path):
        return False, "os.img absent"

    boot_ok, boot_msg = validate_boot_sector()
    if not boot_ok:
        return False, f"Boot sector invalide: {boot_msg}"

    qemu_bins = ["qemu-system-i386", "qemu-system-x86_64"]
    qemu_bin = None
    for qb in qemu_bins:
        try:
            r = subprocess.run(["which", qb], capture_output=True, timeout=5)
            if r.returncode == 0:
                qemu_bin = qb
                break
        except:
            pass

    if not qemu_bin:
        try:
            r = subprocess.run(["qemu-system-i386", "--version"], capture_output=True, timeout=5)
            if r.returncode == 0:
                qemu_bin = "qemu-system-i386"
        except:
            pass

    if not qemu_bin:
        log("QEMU non disponible sur ce runner", "WARN")
        return None, "QEMU non disponible"

    log("Lancement QEMU headless (5s)...", "QEMU")
    try:
        cmd = [
            qemu_bin,
            "-drive", f"format=raw,file={img_path},if=floppy",
            "-boot", "a",
            "-m", "32",
            "-nographic",
            "-no-reboot",
            "-serial", "stdio",
            "-monitor", "none",
            "-d", "int",
            "-D", "/tmp/qemu_maxos.log",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        output = result.stdout + result.stderr

        triple_fault = "triple fault" in output.lower() or "Triple fault" in output
        reboot_loop = output.count("Booting") > 2
        cpu_reset = "cpu_reset" in output.lower()

        if triple_fault or cpu_reset:
            return False, f"Triple fault détecté — kernel crash immédiat"
        if reboot_loop:
            return False, "Boucle de reboot — boot sector ne charge pas le kernel"

        if "/tmp/qemu_maxos.log" and os.path.exists("/tmp/qemu_maxos.log"):
            with open("/tmp/qemu_maxos.log", "r", errors="replace") as f:
                qlog = f.read(2000)
            if "triple fault" in qlog.lower():
                return False, "Triple fault dans log QEMU"

        return True, f"QEMU boot sans crash détecté ({len(output)} chars output)"

    except subprocess.TimeoutExpired:
        return True, "QEMU timeout 5s (normal — kernel tourne)"
    except Exception as e:
        return None, f"Erreur QEMU: {e}"

SKIP_DIRS = {".git", "build", "__pycache__", ".github", "ai_dev", ".vscode",
             "node_modules", "docs", "tests"}
SKIP_FILES = {".DS_Store", "Thumbs.db"}
SRC_EXTS = {".c", ".h", ".asm", ".ld", ".s", ".inc"}

CANONICAL_FILES = [
    "boot/boot.asm", "kernel/kernel_entry.asm", "kernel/kernel.c",
    "kernel/io.h", "kernel/idt.h", "kernel/idt.c", "kernel/isr.asm", "kernel/isr.c",
    "kernel/timer.h", "kernel/timer.c", "kernel/memory.h", "kernel/memory.c",
    "kernel/fault_handler.h", "kernel/fault_handler.c",
    "drivers/screen.h", "drivers/screen.c", "drivers/keyboard.h", "drivers/keyboard.c",
    "drivers/vga.h", "drivers/vga.c", "apps/terminal.h", "apps/terminal.c",
    "Makefile", "linker.ld",
]

def discover_files():
    found = []
    for root, dirs, files in os.walk(REPO_PATH):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f in SKIP_FILES:
                continue
            ext = os.path.splitext(f)[1]
            if ext in SRC_EXTS or f == "Makefile":
                rel = os.path.relpath(os.path.join(root, f), REPO_PATH).replace("\\", "/")
                found.append(rel)
    return sorted(found)

def read_all(force=False):
    af = sorted(set(CANONICAL_FILES + discover_files()))
    h = hashlib.md5()
    for f in af:
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            try:
                st = os.stat(p)
                h.update(f"{f}:{st.st_mtime:.3f}:{st.st_size}".encode())
            except:
                pass
    cur = h.hexdigest()
    if not force and SOURCE_CACHE["hash"] == cur and SOURCE_CACHE["data"]:
        return SOURCE_CACHE["data"]
    src = {}
    for f in af:
        p = os.path.join(REPO_PATH, f)
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    src[f] = fh.read()
            except:
                src[f] = None
        else:
            src[f] = None
    SOURCE_CACHE["hash"] = cur
    SOURCE_CACHE["data"] = src
    return src

def proj_stats(sources):
    files = sum(1 for c in sources.values() if c)
    lines = sum(c.count("\n") for c in sources.values() if c)
    chars = sum(len(c) for c in sources.values() if c)
    by_ext = defaultdict(int)
    for f, c in sources.items():
        if c:
            ext = os.path.splitext(f)[1] or "other"
            by_ext[ext] += 1
    return {"files": files, "lines": lines, "chars": chars, "by_ext": dict(by_ext)}

def build_ctx(sources, max_chars=38000):
    lines = ["=== CODE SOURCE MAXOS ===\n\nFICHIERS PRÉSENTS:\n"]
    for f, c in sources.items():
        lines.append(f"  {'✅' if c else '❌'} {f} ({len(c) if c else 0} chars)\n")
    lines.append("\n")
    ctx = "".join(lines)
    used = len(ctx)
    prio = [
        "kernel/kernel.c", "kernel/kernel_entry.asm", "kernel/io.h",
        "Makefile", "linker.ld", "drivers/screen.h", "drivers/keyboard.h",
        "kernel/idt.h", "kernel/isr.asm", "kernel/fault_handler.h",
    ]
    done = set()
    for f in prio:
        c = sources.get(f, "")
        if not c:
            continue
        block = f"{'=' * 50}\nFICHIER: {f}\n{'=' * 50}\n{c}\n\n"
        if used + len(block) > max_chars:
            ctx += f"[{f}: {len(c)} chars — tronqué]\n"
            done.add(f)
            continue
        ctx += block
        used += len(block)
        done.add(f)
    for f, c in sources.items():
        if f in done or not c:
            continue
        block = f"{'=' * 50}\nFICHIER: {f}\n{'=' * 50}\n{c}\n\n"
        if used + len(block) > max_chars:
            ctx += f"[{f}: {len(c)} chars — tronqué]\n"
            continue
        ctx += block
        used += len(block)
    return ctx

def analyze_quality(sources):
    bad_inc = ["stddef.h", "string.h", "stdlib.h", "stdio.h", "stdint.h",
               "stdbool.h", "stdarg.h", "stdnoreturn.h"]
    bad_sym = ["size_t", "NULL", "bool", "true", "false",
               "uint32_t", "uint8_t", "uint16_t", "int32_t",
               "malloc", "free", "calloc", "realloc",
               "memset", "memcpy", "memmove", "strlen", "strcpy", "strcat",
               "printf", "sprintf", "fprintf", "puts"]
    violations = []
    cf = af = 0
    for fname, content in sources.items():
        if not content:
            continue
        if fname.endswith((".c", ".h")):
            cf += 1
            for i, line in enumerate(content.split("\n"), 1):
                s = line.strip()
                if s.startswith(("//", "/*", "*", "#pragma")):
                    continue
                for inc in bad_inc:
                    if f"#include <{inc}>" in line or f'#include "{inc}"' in line:
                        violations.append(f"{fname}:{i} [INC] {inc}")
                for sym in bad_sym:
                    if re.search(r"\b" + re.escape(sym) + r"\b", line):
                        violations.append(f"{fname}:{i} [SYM] {sym}")
                        break
        elif fname.endswith((".asm", ".s")):
            af += 1
    score = max(0, 100 - len(violations) * 3)
    return {"score": score, "violations": violations[:35], "c_files": cf, "asm_files": af}

class ProjectSnapshot:
    def __init__(self, sources):
        self.sources = sources
        self.signatures = {}
        self.exports = {}
        self.makefile = sources.get("Makefile", "") or ""
        self.files = [f for f, c in sources.items() if c]
        self._parse()

    def _parse(self):
        func_re = re.compile(
            r"^(?:static\s+)?(?:inline\s+)?(?:void|int|char|unsigned\s+\w+|\w+)\s+"
            r"(\w+)\s*\([^)]*\)\s*(?:\{|;)",
            re.MULTILINE
        )
        for fname, content in self.sources.items():
            if not content:
                continue
            if not fname.endswith((".c", ".h")):
                continue
            self.signatures[fname] = {}
            for m in func_re.finditer(content):
                func = m.group(1)
                line = content[max(0, m.start() - 2):m.end()].strip().split("\n")[0]
                self.signatures[fname][func] = line[:120]
        global_re = re.compile(r"^\s*global\s+(\w+)", re.MULTILINE)
        for fname, content in self.sources.items():
            if not content:
                continue
            if not fname.endswith((".asm", ".s")):
                continue
            self.exports[fname] = global_re.findall(content)

    def get_all_func_signatures(self):
        result = {}
        for fname, sigs in self.signatures.items():
            for func, sig in sigs.items():
                result[func] = sig
        return result

    def get_isr_globals(self):
        for fname, exports in self.exports.items():
            if "isr" in fname:
                return exports
        return []

    def check_consistency(self):
        issues = []
        kmain_found = any("kmain" in sigs for sigs in self.signatures.values())
        if not kmain_found:
            issues.append("⚠️ 'kmain' introuvable — kernel_entry.asm doit appeler 'kmain'")
        isr_globals = self.get_isr_globals()
        missing_isr = [f"isr{i}" for i in range(48) if f"isr{i}" not in isr_globals]
        if missing_isr:
            issues.append(f"⚠️ isr.asm manque: {missing_isr[:5]}... ({len(missing_isr)} total)")
        if "os.img" not in self.makefile:
            issues.append("⚠️ Makefile sans règle 'os.img'")
        if "dd" not in self.makefile:
            issues.append("⚠️ Makefile sans commande 'dd' pour créer os.img")
        return issues

    def get_context_for_task(self, task, max_chars=26000):
        needed = set()
        needed.update(task.get("fichiers_a_modifier", []))
        needed.update(task.get("fichiers_a_creer", []))
        for f in list(needed):
            if f.endswith(".c"):
                needed.add(f.replace(".c", ".h"))
            elif f.endswith(".h"):
                needed.add(f.replace(".h", ".c"))
        always = ["kernel/kernel.c", "kernel/kernel_entry.asm", "kernel/io.h",
                  "Makefile", "linker.ld", "kernel/idt.h", "kernel/isr.asm",
                  "drivers/screen.h", "kernel/fault_handler.h", "kernel/timer.h"]
        needed.update(always)
        ctx = ""
        used = 0
        for f in sorted(needed):
            c = self.sources.get(f, "")
            content_show = (c[:14000] if c and len(c) > 14000 else (c or ""))
            block = f"{'=' * 50}\nFICHIER: {f}\n{'=' * 50}\n{content_show if content_show else '[À CRÉER]'}\n\n"
            if used + len(block) > max_chars:
                ctx += f"[{f}: tronqué]\n"
                continue
            ctx += block
            used += len(block)
        return ctx

FILE_START_RE = re.compile(
    r"(?:={3,}|-{3,})\s*FILE\s*:\s*[`'\"]?([A-Za-z0-9_./@-][A-Za-z0-9_./@ -]*?)[`'\"]?\s*(?:={3,}|-{3,})",
    re.IGNORECASE)
FILE_END_RE = re.compile(r"(?:={3,}|-{3,})\s*END\s*(?:FILE)?\s*(?:={3,}|-{3,})", re.IGNORECASE)
FILE_DELETE_RE = re.compile(
    r"(?:={3,}|-{3,})\s*DELETE\s*:\s*[`'\"]?([A-Za-z0-9_./@-][A-Za-z0-9_./@ -]*?)[`'\"]?\s*(?:={3,}|-{3,})",
    re.IGNORECASE)

def parse_ai_files(resp):
    files = {}
    to_del = []
    cur = None
    lines = []
    in_f = False
    for raw_line in resp.split("\n"):
        s = raw_line.strip()
        del_m = FILE_DELETE_RE.match(s)
        if del_m:
            fn = del_m.group(1).strip()
            if fn:
                to_del.append(fn)
            continue
        start_m = FILE_START_RE.match(s)
        if start_m:
            if in_f and cur and lines:
                _commit_file(files, cur, lines)
            fn = start_m.group(1).strip()
            if fn and not fn.startswith("-") and len(fn) > 1:
                cur = fn
                lines = []
                in_f = True
            continue
        if FILE_END_RE.match(s) and in_f:
            if cur and lines:
                _commit_file(files, cur, lines)
            cur = None
            lines = []
            in_f = False
            continue
        if in_f:
            lines.append(raw_line)
    if in_f and cur and lines:
        _commit_file(files, cur, lines)
    if not files and not to_del:
        log(f"Parse: aucun fichier. Début: {resp[:200]}", "WARN")
    return files, to_del

def _commit_file(files_dict, path, lines):
    path = path.strip().strip("`'\"")
    content = "\n".join(lines).strip()
    for fence in ("```c", "```asm", "```nasm", "```makefile", "```ld", "```bash", "```text", "```"):
        if content.startswith(fence):
            content = content[len(fence):].lstrip("\n")
            break
    if content.endswith("```"):
        content = content[:-3].rstrip("\n")
    content = content.strip()
    if content and len(content) > 5:
        files_dict[path] = content
        log(f"Parsé: {path} ({len(content):,}c)")
    else:
        log(f"Parsé vide ignoré: {path}", "WARN")

def write_files(files):
    written = []
    repo_real = os.path.realpath(REPO_PATH) + os.sep
    for path, content in files.items():
        path = path.strip().strip("/").replace("\\", "/")
        full = os.path.realpath(os.path.join(REPO_PATH, path))
        if not (full + os.sep).startswith(repo_real):
            log(f"Path traversal bloqué: {path}", "ERROR")
            continue
        if not content or len(content) < 5:
            log(f"Contenu trop court ignoré: {path}", "WARN")
            continue
        parent = os.path.dirname(full)
        if parent and parent != REPO_PATH:
            os.makedirs(parent, exist_ok=True)
        try:
            with open(full, "w", encoding="utf-8", newline="\n") as f:
                f.write(content)
            written.append(path)
            log(f"Écrit: {path} ({len(content):,}c)")
        except Exception as e:
            log(f"Erreur écriture {path}: {e}", "ERROR")
    SOURCE_CACHE["hash"] = None
    return written

def del_files(paths):
    deleted = []
    repo_real = os.path.realpath(REPO_PATH) + os.sep
    for path in paths:
        path = path.strip().strip("/")
        full = os.path.realpath(os.path.join(REPO_PATH, path))
        if not (full + os.sep).startswith(repo_real):
            log(f"Delete traversal bloqué: {path}", "ERROR")
            continue
        if os.path.exists(full) and os.path.isfile(full):
            os.remove(full)
            deleted.append(path)
            log(f"Supprimé: {path}")
    SOURCE_CACHE["hash"] = None
    return deleted

def backup(paths):
    bak = {}
    for p in paths:
        full = os.path.join(REPO_PATH, p)
        if os.path.exists(full) and os.path.isfile(full):
            try:
                with open(full, "r", encoding="utf-8", errors="ignore") as f:
                    bak[p] = f.read()
            except:
                pass
    return bak

def restore(bak):
    if not bak:
        return
    for p, c in bak.items():
        full = os.path.join(REPO_PATH, p)
        parent = os.path.dirname(full)
        if parent:
            os.makedirs(parent, exist_ok=True)
        try:
            with open(full, "w", encoding="utf-8", newline="\n") as f:
                f.write(c)
        except Exception as e:
            log(f"Erreur restore {p}: {e}", "ERROR")
    log(f"Restauré {len(bak)} fichier(s)")
    SOURCE_CACHE["hash"] = None

OS_MISSION = (
    "MISSION MaxOS: OS bare metal x86 complet, moderne, stable.\n"
    "PROGRESSION: Boot→IDT+PIC→Timer PIT→Mémoire bitmap→VGA→Clavier IRQ→Terminal→GUI"
)

RULES = """╔══ RÈGLES BARE METAL x86 — VIOLATIONS = ÉCHEC BUILD ══╗
║   • boot.asm: JAMAIS 'extern kmain' ou 'call kmain'    ║
║     boot.asm fait jmp 0x10000 — c'est tout             ║
║   • kernel_entry.asm: 'extern kmain' + 'call kmain'    ║
║ INCLUDES INTERDITS: stddef.h string.h stdlib.h stdio.h║
║   stdint.h stdbool.h stdarg.h stdnoreturn.h            ║
║ SYMBOLES INTERDITS: size_t NULL bool true false        ║
║   uint32_t uint8_t uint16_t int32_t                    ║
║   malloc free calloc realloc                           ║
║   memset memcpy memmove strlen strcpy strcat           ║
║   printf sprintf fprintf puts                          ║
║ REMPLACEMENTS: size_t→unsigned int  NULL→0             ║
║   bool/true/false→int/1/0  uint32_t→unsigned int      ║
║   uint8_t→unsigned char  uint16_t→unsigned short      ║
║ TOOLCHAIN:                                             ║
║   GCC: -m32 -ffreestanding -fno-builtin               ║
║        -nostdlib -nostdinc -fno-pic -fno-pie           ║
║   NASM: -f elf (→.o) | -f bin (boot.bin)              ║
║   LD: ld -m elf_i386 -T linker.ld --oformat binary    ║
║ RÈGLES CRITIQUES:                                      ║
║   • kernel/io.h: SEUL fichier avec outb/inb            ║
║   • isr.asm: PAS de %macro/%rep — ÉCRIRE isr0:...     ║
║     isr47: MANUELLEMENT, un par un                     ║
║   • kernel_entry.asm: appelle 'kmain' (pas 'main')    ║
║   • Tout .c nouveau → Makefile OBJS                   ║
║   • ZÉRO commentaire dans le code                     ║
║   • os.img via: dd boot.bin + dd kernel.bin seek=1    ║
║   • NE PAS utiliser 'unsigned_char' (typo fréquente)  ║
║   • EN MODE 32BIT: pas de 'push eip' ou '%eip'        ║
║   • NE PAS inventer: v_put v_str kernel_main           ║
╚════════════════════════════════════════════════════════╝"""

CANONICAL_BOOT_ASM = """\
BITS 16
ORG 0x7C00

start:
    cli
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00
    sti

    mov [boot_drive], dl

    mov ah, 0x02
    mov al, 32
    mov ch, 0
    mov cl, 2
    mov dh, 0
    mov dl, [boot_drive]
    mov bx, 0x1000
    mov es, bx
    mov bx, 0x0000
    int 0x13
    jc disk_error

    cli
    lgdt [gdt_descriptor]
    mov eax, cr0
    or eax, 1
    mov cr0, eax
    jmp 0x08:protected_mode

disk_error:
    mov si, err_msg
.loop:
    lodsb
    or al, al
    jz .done
    mov ah, 0x0E
    int 0x10
    jmp .loop
.done:
    hlt

BITS 32
protected_mode:
    mov ax, 0x10
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    mov esp, 0x90000
    jmp 0x10000

gdt_start:
    dq 0x0000000000000000
    dq 0x00CF9A000000FFFF
    dq 0x00CF92000000FFFF
gdt_end:

gdt_descriptor:
    dw gdt_end - gdt_start - 1
    dd gdt_start

boot_drive: db 0
err_msg: db 'Disk error', 0

times 510-($-$$) db 0
dw 0xAA55
"""

CANONICAL_KERNEL_ENTRY_ASM = """\
BITS 32
global _start
global _stack_top
extern kmain

section .bss
resb 16384
_stack_top:

section .text
_start:
    mov esp, _stack_top
    call kmain
.hang:
    cli
    hlt
    jmp .hang
"""

LINKER_LD = """\
ENTRY(kmain)
OUTPUT_FORMAT(binary)

SECTIONS
{
    . = 0x1000;
    .text   : { *(.text) }
    .data   : { *(.data) }
    .rodata : { *(.rodata) }
    .bss    : { *(.bss) *(COMMON) }
}
"""

def _ensure_build_system():
    mf_path  = os.path.join(REPO_PATH, "Makefile")
    ld_path  = os.path.join(REPO_PATH, "linker.ld")
    boot_path = os.path.join(REPO_PATH, "boot", "boot.asm")
    ke_path   = os.path.join(REPO_PATH, "kernel", "kernel_entry.asm")
    modified  = False

    mf_ok = False
    if os.path.exists(mf_path):
        with open(mf_path, "r") as f:
            mf_content = f.read()
        if "os.img" in mf_content and "dd" in mf_content and "kernel.bin" in mf_content:
            mf_ok = True
    if not mf_ok:
        log("Makefile invalide — injection canonique", "WARN")
        with open(mf_path, "w", newline="\n") as f:
            f.write(CANONICAL_MAKEFILE)
        modified = True

    if not os.path.exists(ld_path):
        log("linker.ld absent — création", "WARN")
        with open(ld_path, "w", newline="\n") as f:
            f.write(LINKER_LD)
        modified = True

    # Vérifier boot.asm — s'il appelle kmain par nom c'est cassé
    boot_broken = False
    if os.path.exists(boot_path):
        with open(boot_path, "r", errors="ignore") as f:
            boot_content = f.read()
        # boot.asm ne doit PAS avoir extern kmain ou call kmain
        if "extern kmain" in boot_content or (
            "call kmain" in boot_content and "BITS 16" in boot_content
        ) or "[org" in boot_content.lower():
            boot_broken = True
    else:
        boot_broken = True

    if boot_broken:
        log("boot.asm cassé ou absent — injection canonique", "WARN")
        os.makedirs(os.path.dirname(boot_path), exist_ok=True)
        with open(boot_path, "w", newline="\n") as f:
            f.write(CANONICAL_BOOT_ASM)
        modified = True

    # Vérifier kernel_entry.asm — doit appeler kmain
    ke_broken = False
    if os.path.exists(ke_path):
        with open(ke_path, "r", errors="ignore") as f:
            ke_content = f.read()
        if "kmain" not in ke_content or "extern kmain" not in ke_content:
            ke_broken = True
    else:
        ke_broken = True

    if ke_broken:
        log("kernel_entry.asm cassé ou absent — injection canonique", "WARN")
        os.makedirs(os.path.dirname(ke_path), exist_ok=True)
        with open(ke_path, "w", newline="\n") as f:
            f.write(CANONICAL_KERNEL_ENTRY_ASM)
        modified = True

    if modified:
        SOURCE_CACHE["hash"] = None
    return modified

def _parse_json_robust(resp):
    if not resp:
        return None
    clean = resp.strip()
    if clean.startswith("```"):
        lines = clean.split("\n")
        end = -1 if lines[-1].strip() == "```" else len(lines)
        clean = "\n".join(lines[1:end]).strip()
    i = clean.find("{")
    j = clean.rfind("}") + 1
    if i < 0 or j <= i:
        return None
    candidate = clean[i:j]
    try:
        return json.loads(candidate)
    except:
        pass
    fixed = re.sub(r',\s*([}\]])', r'\1', candidate)
    try:
        return json.loads(fixed)
    except:
        pass
    fixed2 = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r'\\\\', candidate)
    try:
        return json.loads(fixed2)
    except:
        return None

def default_plan():
    return {
        "score_actuel": 35,
        "niveau_os": "Prototype bare metal",
        "fonctionnalites_presentes": ["Boot x86", "VGA texte 80x25"],
        "fonctionnalites_manquantes_critiques": ["IDT+PIC", "Timer", "Mémoire"],
        "prochaine_milestone": "Kernel stable IDT+Timer+Memory",
        "plan_ameliorations": [
            {
                "nom": "Makefile canonique + os.img garanti",
                "priorite": "CRITIQUE",
                "categorie": "build",
                "fichiers_a_modifier": ["Makefile", "linker.ld"],
                "fichiers_a_creer": [],
                "fichiers_a_supprimer": [],
                "description": (
                    "Makefile: règle os.img avec dd. "
                    "CFLAGS: -m32 -ffreestanding -fno-builtin -nostdlib -nostdinc -fno-pic -fno-pie -I. "
                    "LFLAGS: -m elf_i386 -T linker.ld --oformat binary "
                    "linker.ld: ENTRY(kmain) SECTIONS {. = 0x1000; .text .data .rodata .bss}"
                ),
                "impact_attendu": "os.img bootable à chaque make",
                "complexite": "BASSE",
            },
            {
                "nom": "kernel/io.h + IDT + ISR complet",
                "priorite": "CRITIQUE",
                "categorie": "kernel",
                "fichiers_a_modifier": ["kernel/kernel.c", "Makefile"],
                "fichiers_a_creer": ["kernel/io.h", "kernel/idt.h", "kernel/idt.c", "kernel/isr.asm", "kernel/isr.c"],
                "fichiers_a_supprimer": [],
                "description": (
                    "kernel/io.h: outb/inb static inline. "
                    "kernel/idt.h: struct IDTEntry/IDTPtr + prototypes. "
                    "kernel/idt.c: remap PIC 0x20/0xA0, fill idt[0..47], lidt. "
                    "kernel/isr.asm: BITS 32, global isr0 à isr47, écrire explicitement. "
                    "kernel/isr.c: void isr_handler(unsigned int num, unsigned int err)."
                ),
                "impact_attendu": "IDT fonctionnelle, pas de triple fault",
                "complexite": "HAUTE",
            },
        ],
    }

def diagnose_errors(errs, build_log, snap):
    err_str = "\n".join(errs)
    log_str = build_log[:8000] if build_log else ""
    full_str = err_str + "\n" + log_str
    diagnostics = []
    corrupted = set()
    makefile_broken = False
    needs_reset = False
    auto_fixed_files = {}

    for pattern, solution in KNOWN_FIXES.items():
        if re.search(re.escape(pattern), full_str, re.IGNORECASE):
            diagnostics.append(f"⚡ {solution}")

    if re.search(r"symbol [`']kmain'? not defined", full_str, re.IGNORECASE) or \
       "extern kmain" in full_str and "boot.asm" in full_str or \
       ("call kmain" in full_str and "BITS 16" in full_str):
        diagnostics.append(
            "⚡ CRITIQUE: boot.asm appelle 'kmain' par nom depuis le bootloader 16-bit — "
            "IMPOSSIBLE. boot.asm doit charger le kernel puis 'jmp 0x10000'. "
            "Seul kernel_entry.asm (BITS 32) peut faire 'extern kmain' + 'call kmain'."
        )
        boot_path = os.path.join(REPO_PATH, "boot", "boot.asm")
        ke_path   = os.path.join(REPO_PATH, "kernel", "kernel_entry.asm")
        os.makedirs(os.path.dirname(boot_path), exist_ok=True)
        os.makedirs(os.path.dirname(ke_path),   exist_ok=True)
        with open(boot_path, "w", newline="\n") as f:
            f.write(CANONICAL_BOOT_ASM)
        with open(ke_path, "w", newline="\n") as f:
            f.write(CANONICAL_KERNEL_ENTRY_ASM)
        auto_fixed_files["boot/boot.asm"]          = CANONICAL_BOOT_ASM
        auto_fixed_files["kernel/kernel_entry.asm"] = CANONICAL_KERNEL_ENTRY_ASM
        SOURCE_CACHE["hash"] = None
        log("boot.asm + kernel_entry.asm réinitialisés (kmain fix)", "FIX")
        needs_reset = True

    if re.search(r"unrecognized directive \[org\]", full_str, re.IGNORECASE) or \
       re.search(r"parser: instruction expected", full_str, re.IGNORECASE):
        diagnostics.append(
            "⚡ boot.asm utilise la syntaxe MASM/TASM ([org] ou format incorrect). "
            "NASM utilise 'ORG 0x7C00' sans crochets. Injection du boot.asm canonique."
        )
        boot_path = os.path.join(REPO_PATH, "boot", "boot.asm")
        os.makedirs(os.path.dirname(boot_path), exist_ok=True)
        with open(boot_path, "w", newline="\n") as f:
            f.write(CANONICAL_BOOT_ASM)
        auto_fixed_files["boot/boot.asm"] = CANONICAL_BOOT_ASM
        SOURCE_CACHE["hash"] = None
        log("boot.asm réinitialisé (syntaxe [org] incorrecte)", "FIX")

    isr_globals = snap.get_isr_globals()
    if re.search(r"undefined reference to [`']isr\d+", full_str, re.IGNORECASE):
        missing = [f"isr{i}" for i in range(48) if f"isr{i}" not in isr_globals]
        if missing:
            diagnostics.append(
                f"⚡ isr.asm: {len(missing)} symboles manquants ({missing[:5]}...) — "
                "Écrire isr0:...isr47: EXPLICITEMENT avec 'global isr0'...'global isr47'. "
                "JAMAIS %macro/%rep. Chaque stub doit pousser 0+numéro ou juste le numéro."
            )
            needs_reset = True

    if re.search(r"undefined reference to [`']?main['`]?", full_str, re.IGNORECASE) and \
       "kmain" not in full_str.split("undefined reference")[0]:
        diagnostics.append(
            "⚡ kernel_entry.asm appelle 'main' au lieu de 'kmain'. "
            "Changer 'extern main' → 'extern kmain' et 'call main' → 'call kmain'."
        )
        ke_path = os.path.join(REPO_PATH, "kernel", "kernel_entry.asm")
        if os.path.exists(ke_path):
            with open(ke_path, "r", errors="ignore") as f:
                ke_content = f.read()
            if "extern main" in ke_content or "call main" in ke_content:
                ke_fixed = ke_content.replace("extern main", "extern kmain").replace("call main", "call kmain")
                with open(ke_path, "w", newline="\n") as f:
                    f.write(ke_fixed)
                auto_fixed_files["kernel/kernel_entry.asm"] = ke_fixed
                SOURCE_CACHE["hash"] = None
                log("kernel_entry.asm: main → kmain corrigé automatiquement", "FIX")
        else:
            with open(ke_path, "w", newline="\n") as f:
                f.write(CANONICAL_KERNEL_ENTRY_ASM)
            auto_fixed_files["kernel/kernel_entry.asm"] = CANONICAL_KERNEL_ENTRY_ASM
            SOURCE_CACHE["hash"] = None

    if re.search(r"undefined reference to [`']?kernel_main['`]?", full_str, re.IGNORECASE):
        diagnostics.append(
            "⚡ 'kernel_main' n'existe pas — la fonction d'entrée s'appelle 'kmain'. "
            "Renommer void kernel_main() → void kmain() dans kernel.c ET kernel_entry.asm."
        )
        for fname in ["kernel/kernel.c", "kernel/kmain.c", "kernel/start.c"]:
            fpath = os.path.join(REPO_PATH, fname)
            if os.path.exists(fpath):
                with open(fpath, "r", errors="ignore") as f:
                    content = f.read()
                if "kernel_main" in content:
                    fixed = content.replace("kernel_main", "kmain")
                    with open(fpath, "w", newline="\n") as f:
                        f.write(fixed)
                    auto_fixed_files[fname] = fixed
                    SOURCE_CACHE["hash"] = None
                    log(f"{fname}: kernel_main → kmain corrigé", "FIX")

    if re.search(r"No rule to make target", full_str, re.IGNORECASE) or \
       re.search(r"\*\*\* No rule", full_str, re.IGNORECASE):
        makefile_broken = True
        orphan_re = re.compile(r"No rule to make target [`']([^'`]+\.o)[`']", re.IGNORECASE)
        orphans = orphan_re.findall(full_str)
        if orphans:
            diagnostics.append(
                f"⚡ Makefile référence des .o orphelins: {orphans[:5]} — "
                "Retirer ces objets de OBJS dans le Makefile ou créer les fichiers sources."
            )
            mf_path = os.path.join(REPO_PATH, "Makefile")
            if os.path.exists(mf_path):
                with open(mf_path, "r") as f:
                    mf = f.read()
                for orphan in orphans:
                    base = os.path.basename(orphan).replace(".o", "")
                    for pattern in [f"$(BUILD)/{base}.o", f"build/{base}.o", f"{base}.o"]:
                        mf = mf.replace(" " + pattern, "").replace("\t" + pattern, "")
                with open(mf_path, "w", newline="\n") as f:
                    f.write(mf)
                auto_fixed_files["Makefile"] = mf
                SOURCE_CACHE["hash"] = None
                log(f"Makefile: {len(orphans)} objets orphelins retirés", "FIX")
        else:
            diagnostics.append("⚡ Makefile cassé — vérifier OBJS, VPATH et noms de cibles")
            needs_reset = True

    if re.search(r"Stop\.", full_str) and not makefile_broken:
        makefile_broken = True
        diagnostics.append("⚡ make Stop — Makefile a une erreur de syntaxe ou une dépendance circulaire")

    conflicting_re = re.compile(r"conflicting types for [`'](\w+)[`']", re.IGNORECASE)
    conflicts = set(conflicting_re.findall(full_str))
    for func in conflicts:
        canonical = CANONICAL_SIGNATURES.get(func)
        if canonical:
            diagnostics.append(
                f"⚡ Type conflictuel pour '{func}' — signature EXACTE requise: {canonical}. "
                f"Vérifier TOUS les fichiers .h et .c qui déclarent/définissent '{func}'."
            )
            for fname, content in snap.sources.items():
                if not content or not fname.endswith((".c", ".h")):
                    continue
                if func in content:
                    func_re = re.compile(
                        r"(?:void|int|char|unsigned\s+\w+|\w+)\s+" + re.escape(func) + r"\s*\([^)]*\)",
                        re.MULTILINE
                    )
                    for m in func_re.finditer(content):
                        actual_sig = m.group(0).strip()
                        if actual_sig != canonical.split("{")[0].strip() and actual_sig != canonical:
                            corrupted.add(fname)
        else:
            diagnostics.append(
                f"⚡ Type conflictuel pour '{func}' — aligner toutes les déclarations sur une seule signature."
            )

    missing_header_re = re.compile(r"fatal error: ([^\s:]+\.h): No such file or directory", re.IGNORECASE)
    missing_headers = set(missing_header_re.findall(full_str))
    for header in missing_headers:
        diagnostics.append(
            f"⚡ Header '{header}' introuvable. "
            f"Vérifier le chemin #include et que CFLAGS contient -I. "
            f"Si dans drivers/ → utiliser #include \"drivers/{header}\". "
            f"Si dans kernel/ → utiliser #include \"kernel/{header}\"."
        )
        for fname, content in snap.sources.items():
            if not content:
                continue
            if f'"{header}"' in content or f"<{header}>" in content:
                if os.path.basename(fname).replace(".c", ".h") != header:
                    corrupted.add(fname)

    too_many_re = re.compile(r"too many arguments to function [`'](\w+)[`']", re.IGNORECASE)
    too_few_re  = re.compile(r"too few arguments to function [`'](\w+)[`']", re.IGNORECASE)
    for func in set(too_many_re.findall(full_str)) | set(too_few_re.findall(full_str)):
        canonical = CANONICAL_SIGNATURES.get(func)
        if canonical:
            diagnostics.append(
                f"⚡ Mauvais nombre d'arguments pour '{func}'. "
                f"Signature EXACTE: {canonical}"
            )
        else:
            diagnostics.append(f"⚡ Mauvais nombre d'arguments pour '{func}' — vérifier la déclaration.")

    invented_syms = {
        "kernel_main": "kmain",
        "v_put":       "screen_putchar",
        "v_str":       "screen_write",
        "unsigned_char": "unsigned char",
        "screen_puthex": "screen_write (implémenter hex manuellement)",
        "screen_putstr": "screen_write",
        "vga_putstr":    "screen_write",
        "vga_puts":      "screen_write",
        "con_write":     "screen_write",
        "con_puts":      "screen_write",
        "kprint":        "screen_write",
        "kprintf":       "screen_write (pas de printf bare metal)",
        "panic":         "screen_write + hlt inline",
    }
    for sym, replacement in invented_syms.items():
        if re.search(r"\b" + re.escape(sym) + r"\b", full_str):
            diagnostics.append(
                f"⚡ SYMBOLE INVENTÉ '{sym}' — utiliser '{replacement}' à la place."
            )
            for fname, content in snap.sources.items():
                if content and re.search(r"\b" + re.escape(sym) + r"\b", content):
                    corrupted.add(fname)

    if re.search(r"bad register name [`']%eip[`']", full_str, re.IGNORECASE):
        diagnostics.append(
            "⚡ 'push eip' ou '%eip' invalide en mode 32-bit NASM. "
            "EIP ne peut pas être manipulé directement. "
            "Utiliser 'call $+5 / pop eax' pour obtenir EIP si nécessaire. "
            "Sinon supprimer complètement cette ligne."
        )
        for fname, content in snap.sources.items():
            if content and fname.endswith((".asm", ".s")) and "%eip" in content:
                fpath = os.path.join(REPO_PATH, fname)
                if os.path.exists(fpath):
                    lines = content.split("\n")
                    fixed_lines = [l for l in lines if "%eip" not in l and "push eip" not in l.lower()]
                    fixed_content = "\n".join(fixed_lines)
                    with open(fpath, "w", newline="\n") as f:
                        f.write(fixed_content)
                    auto_fixed_files[fname] = fixed_content
                    SOURCE_CACHE["hash"] = None
                    log(f"{fname}: lignes %eip supprimées automatiquement", "FIX")

    if re.search(r"multiple definition of [`'](\w+)[`']", full_str, re.IGNORECASE):
        multi_re = re.compile(r"multiple definition of [`'](\w+)[`']", re.IGNORECASE)
        multis = set(multi_re.findall(full_str))
        for sym in multis:
            if sym in ("outb", "inb"):
                diagnostics.append(
                    f"⚡ '{sym}' défini en plusieurs endroits. "
                    "outb/inb doivent être UNIQUEMENT dans kernel/io.h comme static inline. "
                    "Retirer toute autre définition de outb/inb dans les .c"
                )
            else:
                diagnostics.append(
                    f"⚡ '{sym}' défini plusieurs fois. "
                    "Une seule définition autorisée — les autres fichiers doivent déclarer 'extern'."
                )

    if re.search(r"undefined reference to [`']outb[`']|undefined reference to [`']inb[`']", full_str):
        diagnostics.append(
            "⚡ outb/inb non trouvés — vérifier que kernel/io.h est inclus dans le fichier concerné. "
            "#include \"kernel/io.h\" ou #include \"io.h\" selon VPATH."
        )

    if re.search(r"ld:.*cannot find|ld:.*no such file", full_str, re.IGNORECASE):
        diagnostics.append(
            "⚡ Linker ne trouve pas un fichier .o ou .bin. "
            "Vérifier que tous les fichiers listés dans Makefile existent et sont compilés."
        )

    if re.search(r"BITS 16.*extern|extern.*BITS 16", full_str, re.DOTALL | re.IGNORECASE):
        diagnostics.append(
            "⚡ 'extern' utilisé dans du code BITS 16 — impossible. "
            "En mode 16-bit (bootloader) on ne peut pas appeler des fonctions C par nom. "
            "Seul kernel_entry.asm en BITS 32 peut utiliser 'extern'."
        )

    if re.search(r"linker command failed|cannot open output file.*kernel\.bin", full_str, re.IGNORECASE):
        diagnostics.append(
            "⚡ Erreur finale du linker — vérifier linker.ld: "
            "ENTRY(kmain), . = 0x1000, sections .text .data .rodata .bss présentes. "
            "Vérifier que tous les .o sont passés au linker."
        )

    if re.search(r"format of input file.*not recognized|file not recognized", full_str, re.IGNORECASE):
        diagnostics.append(
            "⚡ Un fichier .o a un format incorrect. "
            "Vérifier que nasm utilise -f elf (pas -f bin) pour kernel_entry.asm et isr.asm. "
            "boot.asm utilise -f bin."
        )

    if re.search(r"unknown type name [`']unsigned_char[`']", full_str, re.IGNORECASE):
        diagnostics.append(
            "⚡ 'unsigned_char' est une typo — écrire 'unsigned char' avec un espace."
        )
        for fname, content in snap.sources.items():
            if not content:
                continue
            if "unsigned_char" in content:
                fpath = os.path.join(REPO_PATH, fname)
                if os.path.exists(fpath):
                    fixed = content.replace("unsigned_char", "unsigned char")
                    with open(fpath, "w", newline="\n") as f:
                        f.write(fixed)
                    auto_fixed_files[fname] = fixed
                    SOURCE_CACHE["hash"] = None
                    log(f"{fname}: unsigned_char → unsigned char corrigé", "FIX")

    if re.search(r"implicit declaration of function", full_str, re.IGNORECASE):
        impl_re = re.compile(r"implicit declaration of function [`'](\w+)[`']", re.IGNORECASE)
        implicit_funcs = set(impl_re.findall(full_str))
        for func in implicit_funcs:
            canonical = CANONICAL_SIGNATURES.get(func)
            if canonical:
                diagnostics.append(
                    f"⚡ '{func}' utilisé sans déclaration. "
                    f"Inclure le bon header. Signature: {canonical}"
                )
            else:
                diagnostics.append(
                    f"⚡ '{func}' utilisé sans déclaration — inclure le header approprié "
                    f"ou déclarer 'extern {func}(...)' avant utilisation."
                )

    if re.search(r"timeout", full_str, re.IGNORECASE) and "180s" in full_str:
        diagnostics.append(
            "⚡ Build timeout 180s — le Makefile a peut-être une boucle infinie ou dépendance circulaire. "
            "Reset du Makefile recommandé."
        )
        makefile_broken = True
        needs_reset = True

    if re.search(r"error:.*undeclared.*first use", full_str, re.IGNORECASE):
        undecl_re = re.compile(r"[`'](\w+)[`'].*undeclared", re.IGNORECASE)
        undecl = set(undecl_re.findall(full_str))
        for sym in undecl:
            canonical = CANONICAL_SIGNATURES.get(sym)
            if canonical:
                diagnostics.append(
                    f"⚡ '{sym}' non déclaré — inclure son header. Signature: {canonical}"
                )
            elif sym in ("TASK_BLOCKED", "TASK_RUNNING", "TASK_READY"):
                diagnostics.append(
                    f"⚡ '{sym}' non déclaré — inclure kernel/task.h qui définit ces constantes."
                )
            elif sym in ("scheduler_ticks", "task_list"):
                diagnostics.append(
                    f"⚡ '{sym}' non déclaré — inclure kernel/task.h et vérifier que task.c est dans Makefile."
                )

    mentioned_files_re = re.compile(r"(\w[\w/\.]+\.(?:c|h|asm|s))")
    mentioned = set(mentioned_files_re.findall(err_str))
    for f in mentioned:
        if any(bad in f for bad in ["unsigned_char", "kernel_main", "v_put", "v_str"]):
            corrupted.add(f)

    if len(errs) > 15 and not diagnostics:
        needs_reset = True
        diagnostics.append(
            f"⚡ {len(errs)} erreurs sans diagnostic connu — "
            "reset Makefile + linker.ld + boot.asm + kernel_entry.asm recommandé."
        )

    if len(errs) > 25:
        needs_reset = True
        makefile_broken = True
        diagnostics.append(
            f"⚡ {len(errs)} erreurs — projet très cassé. "
            "Reset complet du système de build recommandé."
        )

    if auto_fixed_files:
        log(f"Diagnose: {len(auto_fixed_files)} fichier(s) corrigés automatiquement: {list(auto_fixed_files.keys())[:5]}", "FIX")
        diagnostics.insert(0, f"✅ Auto-corrigé: {', '.join(list(auto_fixed_files.keys())[:5])}")

    unique_diagnostics = list(dict.fromkeys(diagnostics))

    return {
        "diagnostics":      unique_diagnostics,
        "corrupted_files":  list(corrupted),
        "makefile_broken":  makefile_broken,
        "needs_reset":      needs_reset,
        "auto_fixed_files": auto_fixed_files,
    }
def _build_signatures_block(snap):
    all_sigs = snap.get_all_func_signatures()
    lines = ["=== SIGNATURES CANONIQUES (utiliser EXACTEMENT) ===\n"]
    for func, sig in CANONICAL_SIGNATURES.items():
        match = "✅" if func in all_sigs else "❌"
        lines.append(f"{match} {func}: {sig}")
        if func in all_sigs and all_sigs[func] != sig:
            lines.append(f"  ACTUEL: {all_sigs[func]}")
    lines.append("\n=== EXPORTS ASM ===")
    isr_g = snap.get_isr_globals()
    lines.append(f"isr.asm globals: {isr_g[:5]}...({len(isr_g)} total)")
    return "\n".join(lines)

def phase_analyse(context, stats, snap, history):
    log("=== PHASE 1: ANALYSE PROJET ===")
    consistency = snap.check_consistency()
    hist_summary = _history_summary(history)
    disc_now("🔍 Analyse en cours",
             f"`{stats['files']}` fichiers | `{stats['lines']:,}` lignes", 0x5865F2)
    consistency_str = ""
    if consistency:
        consistency_str = "\nPROBLÈMES DÉTECTÉS:\n" + "\n".join(consistency) + "\n"
    prompt = (
        f"Tu es un expert OS bare metal x86. Retourne UNIQUEMENT du JSON valide.\n\n"
        f"{RULES}\n\n{OS_MISSION}\n\n"
        f"HISTORIQUE PROJET:\n{hist_summary}\n\n"
        f"{consistency_str}"
        f"CONTEXT:\n{context[:15000]}\n\n"
        f"STATS: {stats['files']} fichiers, {stats['lines']} lignes\n\n"
        "IMPORTANT: Commence directement par { sans aucun texte avant.\n"
        '{"score_actuel":35,"niveau_os":"desc","fonctionnalites_presentes":["f1"],'
        '"fonctionnalites_manquantes_critiques":["f2"],"prochaine_milestone":"m",'
        '"plan_ameliorations":[{"nom":"N","priorite":"CRITIQUE","categorie":"kernel",'
        '"fichiers_a_modifier":["f"],"fichiers_a_creer":["g"],"fichiers_a_supprimer":[],'
        '"description":"specs précises","impact_attendu":"r","complexite":"HAUTE"}]}'
    )
    resp = ai_call(prompt, max_tokens=3500, timeout=70, tag="analyse")
    if not resp:
        log("Analyse IA indisponible → plan défaut", "WARN")
        return default_plan()
    result = _parse_json_robust(resp)
    if result and isinstance(result.get("plan_ameliorations"), list) and result["plan_ameliorations"]:
        log(f"Analyse OK: score={result.get('score_actuel', '?')} | {len(result['plan_ameliorations'])} tâche(s)", "OK")
        return result
    log("JSON invalide → plan défaut", "WARN")
    return default_plan()

def impl_prompt(task, ctx, snap, consistency_issues):
    nom = task.get("nom", "?")
    cat = task.get("categorie", "?")
    cx = task.get("complexite", "MOYENNE")
    desc = task.get("description", "")
    fmod = task.get("fichiers_a_modifier", [])
    fnew = task.get("fichiers_a_creer", [])
    fdel = task.get("fichiers_a_supprimer", [])
    sig_block = _build_signatures_block(snap)
    consist_str = ""
    if consistency_issues:
        consist_str = "\nPROBLÈMES EXISTANTS À CORRIGER:\n" + "\n".join(consistency_issues) + "\n"
    return (
        f"{RULES}\n\n"
        f"{sig_block}\n\n"
        f"{'=' * 60}\n"
        f"TÂCHE: {nom}\nCATÉGORIE: {cat} | COMPLEXITÉ: {cx}\n"
        f"FICHIERS À MODIFIER: {fmod}\n"
        f"FICHIERS À CRÉER: {fnew}\n"
        f"FICHIERS À SUPPRIMER: {fdel}\n"
        f"{'=' * 60}\n\n"
        f"SPÉCIFICATIONS:\n{desc}\n\n"
        f"{consist_str}\n"
        f"CODE EXISTANT:\n{ctx}\n\n"
        f"{'=' * 60}\n"
        "CONTRAINTES ABSOLUES:\n"
        "1. isr.asm: JAMAIS %macro/%rep — isr0:...isr47: EXPLICITEMENT un par un\n"
        "2. 'global isr0' jusqu'à 'global isr47' OBLIGATOIRE dans isr.asm\n"
        "3. kernel_entry.asm appelle 'kmain' JAMAIS 'main' ou 'kernel_main'\n"
        "4. outb/inb: UNIQUEMENT dans kernel/io.h static inline\n"
        "5. Makefile DOIT produire os.img via dd (boot.bin seek=0, kernel.bin seek=1)\n"
        "6. Tout nouveau .c → Makefile SRCS_C ET VPATH\n"
        "7. ZÉRO commentaire, code 100% complet\n"
        "8. NE PAS inventer de noms: v_put v_str kernel_main unsigned_char\n"
        "9. screen_write prend 2 args: (const char*, unsigned char)\n"
        "10. fault_handler prend 2 args: (unsigned int num, unsigned int err)\n\n"
        "FORMAT DE RÉPONSE:\n"
        "=== FILE: chemin/fichier.ext ===\n[code complet]\n=== END FILE ===\n\n"
        "GÉNÈRE MAINTENANT:"
    )

def auto_fix(build_log, errs, gen_files, bak, model, snap, max_att=4):
    log(f"Auto-fix: {len(errs)} erreur(s)", "FIX")
    _CYCLE_STATS["auto_fixes"] += 1
    cur_log = build_log
    cur_errs = errs
    last_errs_key = None

    for att in range(1, max_att + 1):
        if not cur_errs:
            log(f"Fix {att}: 0 erreurs mais build fail — reset Makefile", "WARN")
            _ensure_build_system()
            ok2, cur_log2, cur_errs2 = make_build()
            if ok2:
                ensure_osimg()
                _CYCLE_STATS["auto_fix_success"] += 1
                return True, {"attempts": att, "fixed_files": ["Makefile"]}
            cur_errs = cur_errs2 if cur_errs2 else ["build fail non résolu"]
            break

        log(f"Fix {att}/{max_att} — {len(cur_errs)} err", "FIX")
        disc_log(f"🔧 Fix {att}/{max_att}",
                 f"`{len(cur_errs)}` erreur(s)\n" +
                 "\n".join(f"`{e[:60]}`" for e in cur_errs[:3]),
                 0x00AAFF)

        errs_key = "|".join(sorted(cur_errs[:5]))
        if errs_key == last_errs_key and att >= 2:
            log("Fix: mêmes erreurs en boucle — reset Makefile", "WARN")
            _ensure_build_system()
            time.sleep(3)
        last_errs_key = errs_key

        current_sources = read_all()
        snap_fix = ProjectSnapshot(current_sources)
        diag = diagnose_errors(cur_errs, cur_log, snap_fix)

        if diag["makefile_broken"]:
            log("Fix: Makefile cassé → reset canonique", "WARN")
            _ensure_build_system()

        curr_files = {}
        for p in gen_files:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp) and os.path.isfile(fp):
                try:
                    with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                        curr_files[p] = f.read()[:12000]
                except:
                    pass

        critical = ["kernel/isr.asm", "kernel/kernel_entry.asm", "kernel/io.h",
                    "Makefile", "kernel/idt.h", "drivers/screen.h",
                    "kernel/fault_handler.h", "kernel/timer.h"]
        for p in critical:
            if p not in curr_files:
                fp = os.path.join(REPO_PATH, p)
                if os.path.exists(fp):
                    try:
                        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                            curr_files[p] = f.read()[:8000]
                    except:
                        pass

        file_ctx = "".join(f"--- {p} ---\n{c}\n\n" for p, c in curr_files.items())
        err_str = "\n".join(cur_errs[:20])
        log_tail = cur_log[-2500:] if len(cur_log) > 2500 else cur_log
        sig_block = _build_signatures_block(snap_fix)

        prompt = (
            f"{RULES}\n\n"
            f"{sig_block}\n\n"
            f"ERREURS:\n```\n{err_str}\n```\n\n"
            f"LOG (fin):\n```\n{log_tail}\n```\n\n"
            f"DIAGNOSTICS AUTOMATIQUES:\n" +
            "\n".join(diag["diagnostics"] or ["Aucun diagnostic automatique"]) +
            f"\n\nFICHIERS ACTUELS:\n{file_ctx}\n\n"
            "CORRIGER TOUTES LES ERREURS. Code 100% complet.\n"
            "RÈGLES FIX:\n"
            "- undefined reference to isr0 → réécrire isr.asm complet avec global isr0..isr47\n"
            "- undefined reference to main → kernel_entry.asm doit appeler kmain\n"
            "- conflicting types → aligner avec SIGNATURES CANONIQUES\n"
            "- No such file .h → corriger #include path\n"
            "- No rule to make target → corriger Makefile SRCS_C et VPATH\n"
            "- bad register name %eip → supprimer cette ligne\n"
            "- v_put/v_str → remplacer par screen_putchar/screen_write\n"
            "- kernel_main → remplacer par kmain\n\n"
            "FORMAT:\n=== FILE: fichier ===\n[code]\n=== END FILE ==="
        )

        resp = ai_call(prompt, max_tokens=32768, timeout=130, tag=f"fix/{att}")
        if not resp:
            time.sleep(min(8 * (2 ** (att - 1)), 45))
            continue

        new_files, _ = parse_ai_files(resp)
        if not new_files:
            log(f"Fix {att}: parse vide", "WARN")
            time.sleep(min(5 * (2 ** (att - 1)), 30))
            continue

        write_files(new_files)
        ok, cur_log, cur_errs = make_build()

        if ok:
            ensure_osimg()
            m_u = alive()[0]["model"] if alive() else model
            git_push("fix: build", list(new_files.keys()), f"auto-fix {len(errs)}→0", m_u)
            disc_now("🔧 Fix ✅", f"**{len(errs)} err** → **0** en {att} tentative(s)", 0x00AAFF)
            _CYCLE_STATS["auto_fix_success"] += 1
            return True, {"attempts": att, "fixed_files": list(new_files.keys())}

        log(f"Fix {att}: {len(cur_errs)} erreur(s) restantes", "WARN")
        time.sleep(min(6 * (2 ** (att - 1)), 35))

    _CYCLE_STATS["auto_fix_fail"] += 1
    return False, {"attempts": max_att, "remaining_errors": cur_errs[:5]}

def pre_flight_check():
    log("Pre-flight: vérification build initial...", "BUILD")
    _ensure_build_system()
    ok, log_text, errs = make_build()
    if ok:
        ensure_osimg()
        boot_ok, boot_msg = validate_boot_sector()
        log(f"Boot sector: {boot_msg}", "OK" if boot_ok else "WARN")
        img_path = os.path.join(REPO_PATH, "os.img")
        if os.path.exists(img_path):
            log(f"os.img: {os.path.getsize(img_path)} bytes ✅", "OK")
        log("Pre-flight: build OK ✅", "OK")
        return True, []
    log(f"Pre-flight: build cassé ({len(errs)} err)", "WARN")
    disc_now("⚠️ Build pré-existant cassé",
             f"`{len(errs)}` erreur(s)\n" + "\n".join(f"`{e[:75]}`" for e in errs[:4]),
             0xFF6600)
    sources = read_all(force=True)
    snap = ProjectSnapshot(sources)
    fixed, _ = auto_fix(log_text, errs, [], {}, "?", snap, max_att=2)
    if fixed:
        log("Pre-flight: build réparé ✅", "OK")
        return True, []
    return False, errs

def implement(task, sources, snap, i, total):
    nom = task.get("nom", f"Tâche {i}")
    cat = task.get("categorie", "?")
    prio = task.get("priorite", "?")
    cx = task.get("complexite", "MOYENNE")
    desc = task.get("description", "")
    f_mod = task.get("fichiers_a_modifier", [])
    f_new = task.get("fichiers_a_creer", [])
    model = alive()[0]["model"] if alive() else "?"

    log(f"\n{'=' * 56}\n[{i}/{total}] [{prio}] {nom}\n{'=' * 56}")
    consistency_issues = snap.check_consistency()

    disc_now(f"🚀 [{i}/{total}] {nom[:55]}",
             f"```\n{pbar(int((i - 1) / total * 100))}\n```\n{desc[:280]}", 0xFFA500,
             [{"name": "🎯", "value": prio, "inline": True},
              {"name": "📁", "value": cat, "inline": True},
              {"name": "⚙️", "value": cx, "inline": True},
              {"name": "📝 Modifier", "value": "\n".join(f"`{f}`" for f in f_mod[:5]) or "—", "inline": True},
              {"name": "✨ Créer", "value": "\n".join(f"`{f}`" for f in f_new[:5]) or "—", "inline": True},
              {"name": "🔑 Providers", "value": prov_summary()[:400], "inline": False}])

    t0 = time.time()
    ctx = snap.get_context_for_task(task)
    max_tok = {"HAUTE": 32768, "MOYENNE": 24576, "BASSE": 12288, "TRES HAUTE": 32768}.get(cx, 24576)
    prompt = impl_prompt(task, ctx, snap, consistency_issues)
    resp = ai_call(prompt, max_tokens=max_tok, timeout=200, tag=f"impl/{nom[:16]}")
    elapsed = round(time.time() - t0, 1)

    if not resp:
        disc_now(f"❌ [{i}/{total}] {nom[:50]}", f"Providers indisponibles après {elapsed}s", 0xFF4444)
        return False, [], [], {"nom": nom, "elapsed": elapsed, "result": "ai_fail", "errors": [], "model": model}

    files, to_del = parse_ai_files(resp)
    if not files and not to_del:
        disc_now(f"❌ [{i}/{total}] {nom[:50]}",
                 f"Réponse {len(resp):,}c mais aucun fichier", 0xFF6600,
                 [{"name": "Début", "value": f"```\n{resp[:300]}\n```", "inline": False}])
        return False, [], [], {"nom": nom, "elapsed": elapsed, "result": "parse_empty", "errors": [], "model": model}

    disc_log(f"📁 {len(files)} fichier(s)",
             "\n".join(f"`{f}` → {len(c):,}c" for f, c in list(files.items())[:10]), 0x00AAFF)

    bak_f = backup(list(files.keys()))
    written = write_files(files)
    deleted = del_files(to_del)
    if not written and not deleted:
        return False, [], [], {"nom": nom, "elapsed": elapsed, "result": "no_files_written", "errors": [], "model": model}

    ok, build_log, errs = make_build()

    if ok:
        ensure_osimg()
        boot_ok, boot_msg = validate_boot_sector()
        qemu_ok, qemu_msg = run_qemu_test()
        img_ok = os.path.exists(os.path.join(REPO_PATH, "os.img"))
        pushed, sha, commit = git_push(nom, written + deleted, desc, model)
        total_elapsed = round(time.time() - t0, 1)

        qemu_str = "✅ Boot OK" if qemu_ok else ("⚠️ Non testé" if qemu_ok is None else f"❌ {qemu_msg[:40]}")

        if pushed and sha:
            m = {"nom": nom, "elapsed": total_elapsed, "result": "success", "sha": sha,
                 "files": written + deleted, "model": model, "fix_count": 0,
                 "img_ok": img_ok, "boot_ok": boot_ok, "qemu_ok": qemu_ok}
            disc_now(f"✅ [{i}/{total}] {nom[:50]}",
                     f"```\n{pbar(int(i / total * 100))}\n```\nCommit: `{sha}`\nos.img: {'✅' if img_ok else '❌'}",
                     0x00FF88,
                     [{"name": "⏱️", "value": f"{total_elapsed:.0f}s", "inline": True},
                      {"name": "📁", "value": str(len(written + deleted)), "inline": True},
                      {"name": "🤖", "value": model[:30], "inline": True},
                      {"name": "💾 os.img", "value": "✅ Bootable" if img_ok else "❌ Manquant", "inline": True},
                      {"name": "🔐 Boot", "value": boot_msg[:60], "inline": True},
                      {"name": "💻 QEMU", "value": qemu_str, "inline": True}])
            return True, written, deleted, m

        elif pushed and sha is None:
            disc_log(f"✅ [{i}/{total}] {nom[:50]} (déjà à jour)", "", 0x00AA44)
            return True, [], [], {"nom": nom, "elapsed": total_elapsed, "result": "success_no_change",
                                   "sha": git_sha(), "files": [], "model": model, "fix_count": 0}
        else:
            restore(bak_f)
            return False, [], [], {"nom": nom, "elapsed": elapsed, "result": "push_fail", "errors": [], "model": model}

    snap_current = ProjectSnapshot(read_all())
    fixed, fix_meta = auto_fix(build_log, errs, list(files.keys()), bak_f, model, snap_current)

    if fixed:
        total_elapsed = round(time.time() - t0, 1)
        fc = fix_meta.get("attempts", 0)
        img_ok = os.path.exists(os.path.join(REPO_PATH, "os.img"))
        boot_ok, boot_msg = validate_boot_sector()
        qemu_ok, qemu_msg = run_qemu_test()
        m = {"nom": nom, "elapsed": total_elapsed, "result": "success_after_fix",
             "sha": git_sha(), "files": written + deleted, "model": model, "fix_count": fc,
             "img_ok": img_ok, "boot_ok": boot_ok, "qemu_ok": qemu_ok}
        disc_now(f"✅ [{i}/{total}] {nom[:50]} (fix×{fc})",
                 f"```\n{pbar(int(i / total * 100))}\n```\nos.img: {'✅' if img_ok else '❌'}",
                 0x00BB66,
                 [{"name": "⏱️", "value": f"{total_elapsed:.0f}s", "inline": True},
                  {"name": "🔧", "value": f"{fc} fix", "inline": True},
                  {"name": "🤖", "value": model[:30], "inline": True},
                  {"name": "💻 QEMU", "value": qemu_msg[:50] if qemu_ok is not None else "Non testé", "inline": True}])
        return True, written, deleted, m

    restore(bak_f)
    for p in written:
        if p not in bak_f:
            fp = os.path.join(REPO_PATH, p)
            if os.path.exists(fp) and os.path.isfile(fp):
                try:
                    os.remove(fp)
                except:
                    pass
    SOURCE_CACHE["hash"] = None
    total_elapsed = round(time.time() - t0, 1)
    remaining_errs = fix_meta.get("remaining_errors", errs[:5])
    es = "\n".join(f"`{e[:80]}`" for e in remaining_errs[:5])
    disc_now(f"❌ [{i}/{total}] {nom[:50]}",
             f"Build fail après {fix_meta.get('attempts', 0)} fix(es) — restauré",
             0xFF4444,
             [{"name": "Erreurs", "value": es[:900] or "?", "inline": False},
              {"name": "⏱️", "value": f"{total_elapsed:.0f}s", "inline": True}])
    return False, [], [], {"nom": nom, "elapsed": total_elapsed, "result": "build_fail",
                           "errors": remaining_errs[:5], "model": model}

BOT_LOGINS = frozenset({"MaxOS-AI-Bot", "github-actions[bot]", "dependabot[bot]", "maxos-ai[bot]"})

def _bot_already_commented(n):
    comments = gh_issue_comments(n)
    return any(c.get("user", {}).get("login", "") in BOT_LOGINS for c in (comments or []))

def handle_issues(ms_cache=None):
    if ms_cache is None:
        ms_cache = {}
    issues = gh_open_issues()
    if not issues:
        log("Issues: aucune")
        return ms_cache
    log(f"Issues: {len(issues)} ouverte(s)")
    treated = 0
    for issue in issues[:10]:
        n = issue.get("number")
        title = issue.get("title", "")
        author = issue.get("user", {}).get("login", "")
        body_t = (issue.get("body", "") or "")[:1200]
        labels = [l.get("name", "") for l in issue.get("labels", [])]
        if issue.get("state") != "open":
            continue
        if author in BOT_LOGINS:
            continue
        if _bot_already_commented(n):
            continue
        if not watchdog():
            break
        log(f"Issue #{n}: {title[:65]}")

        sources = read_all()
        snap = ProjectSnapshot(sources)
        consistency = snap.check_consistency()
        proj_context = f"Score actuel: ~{35}. Fichiers: {len([f for f,c in sources.items() if c])}."
        if consistency:
            proj_context += " Problèmes: " + "; ".join(consistency[:3])

        prompt = (
            f"Tu es le bot GitHub MaxOS, assistant technique expert OS bare metal x86.\n"
            f"CONTEXTE PROJET: {proj_context}\n\n"
            f"ISSUE #{n}\nTitre: {title}\nAuteur: {author}\n"
            f"Labels: {', '.join(labels) or 'aucun'}\nCorps:\n{body_t}\n\n"
            f"{RULES}\n\n"
            "Analyse cette issue et réponds de façon TRÈS UTILE et TECHNIQUE en français. "
            "Si c'est un bug boot/qemu, explique précisément les causes possibles et solutions. "
            "Si c'est une demande de feature, explique si c'est dans la roadmap. "
            "Si l'utilisateur demande 'tu vas modifier le code?', dis OUI avec les fichiers concernés.\n\n"
            'JSON valide uniquement:\n{"type":"bug|enhancement|question|invalid",'
            '"priority":"critical|high|medium|low","component":"kernel|driver|app|build|doc|other",'
            '"labels_add":["bug"],"action":"respond|close|label_only",'
            '"response":"réponse DÉTAILLÉE et UTILE en français (min 3 phrases, max 15)",'
            '"auto_fix_possible":true|false,"files_concerned":["kernel/boot.asm"]}'
        )
        a = _parse_json_robust(ai_call(prompt, max_tokens=1200, timeout=50, tag=f"issue/{n}"))
        if not a:
            continue
        action = a.get("action", "label_only")
        lbl_add = [l for l in a.get("labels_add", []) if l in STANDARD_LABELS]
        if "ai-reviewed" not in lbl_add:
            lbl_add.append("ai-reviewed")
        if lbl_add:
            gh_add_labels(n, lbl_add)
        resp_t = a.get("response", "")
        auto_fix_possible = a.get("auto_fix_possible", False)
        files_concerned = a.get("files_concerned", [])

        if resp_t and action in ("respond", "close"):
            comment_body = f"## 🤖 MaxOS AI — Analyse #{n}\n\n{resp_t}\n\n"
            if auto_fix_possible and files_concerned:
                comment_body += f"\n**🔧 Fix automatique possible** sur: {', '.join(f'`{f}`' for f in files_concerned[:5])}\n"
                comment_body += "Le bot tentera de corriger lors du prochain cycle CI.\n"
            comment_body += f"\n---\n*MaxOS AI v{VERSION} | Modèle: {alive()[0]['model'][:30] if alive() else '?'}*"
            gh_post_comment(n, comment_body)

        if action == "close":
            gh_close_issue(n, "completed")

        disc_log(f"🎫 Issue #{n}", f"**{title[:45]}** | `{action}` | fix={auto_fix_possible}", 0x5865F2)
        treated += 1
        time.sleep(1)

    log(f"Issues: {treated} traitée(s)")
    return ms_cache

def create_bot_issues(sources, snap, analyse):
    if not GH_TOKEN:
        return
    existing = gh_open_issues()
    existing_titles = {i.get("title", "").lower() for i in existing}
    consistency = snap.check_consistency()
    score = analyse.get("score_actuel", 35)
    issues_to_create = []

    for problem in consistency:
        clean = problem.replace("⚠️ ", "").strip()
        title = f"[AUTO] {clean[:80]}"
        if title.lower() not in existing_titles:
            issues_to_create.append({
                "title": title,
                "body": (
                    f"## 🤖 Issue générée automatiquement par MaxOS AI\n\n"
                    f"**Problème détecté:** {clean}\n\n"
                    f"**Score actuel:** {score}/100\n\n"
                    f"**Action requise:** Ce problème sera corrigé lors du prochain cycle de build.\n\n"
                    f"---\n*MaxOS AI v{VERSION}*"
                ),
                "labels": ["ai-generated", "needs-fix"],
            })

    boot_ok, boot_msg = validate_boot_sector()
    if not boot_ok:
        title = f"[BUG] Boot sector invalide: {boot_msg[:60]}"
        if title.lower() not in existing_titles:
            issues_to_create.append({
                "title": title,
                "body": (
                    f"## 🤖 Boot sector invalide\n\n"
                    f"**Détail:** {boot_msg}\n\n"
                    f"**Impact:** os.img non bootable dans QEMU\n\n"
                    f"**Commande test:**\n```\nqemu-system-i386 -drive format=raw,file=os.img,if=floppy -boot a -m 32\n```\n\n"
                    f"**Fix attendu:** Le Makefile doit produire os.img avec signature 0xAA55 à l'offset 510.\n\n"
                    f"---\n*MaxOS AI v{VERSION}*"
                ),
                "labels": ["ai-generated", "bug", "boot"],
            })

    for issue_data in issues_to_create[:3]:
        result = gh_create_issue(issue_data["title"], issue_data["body"], issue_data["labels"])
        if result:
            log(f"Issue créée: #{result.get('number')} — {issue_data['title'][:50]}", "OK")
        time.sleep(0.5)

def handle_stale(days_stale=21, days_close=7):
    issues = gh_open_issues()
    now = time.time()
    marked = closed = 0
    for issue in issues:
        n = issue.get("number")
        upd = issue.get("updated_at", "")
        labels = [l.get("name", "") for l in issue.get("labels", [])]
        author = issue.get("user", {}).get("login", "")
        if author in BOT_LOGINS:
            continue
        if any(l in labels for l in ("wontfix", "security", "bug")):
            continue
        is_stale = "stale" in labels
        try:
            upd_ts = datetime.strptime(upd, "%Y-%m-%dT%H:%M:%SZ").timestamp()
        except:
            continue
        age = now - upd_ts
        if age >= (days_stale + days_close) * 86400 and is_stale:
            gh_post_comment(n, f"🤖 Fermeture après **{int(age / 86400)}j** d'inactivité.")
            gh_close_issue(n, "not_planned")
            closed += 1
        elif age >= days_stale * 86400 and not is_stale:
            gh_add_labels(n, ["stale"])
            gh_post_comment(n, f"⏰ Inactive depuis **{int(age / 86400)}j**. Fermeture dans {days_close}j.")
            marked += 1
    if marked + closed:
        log(f"Stale: {marked} marquées, {closed} fermées")

def handle_prs():
    prs = gh_open_prs()
    if not prs:
        log("PRs: aucune")
        return
    log(f"PRs: {len(prs)} ouverte(s)")
    reviewed = 0
    for pr in prs[:5]:
        n = pr.get("number")
        title = pr.get("title", "")
        author = pr.get("user", {}).get("login", "")
        if pr.get("state") != "open":
            continue
        if author in BOT_LOGINS:
            continue
        revs = gh_pr_reviews(n)
        if any(r.get("user", {}).get("login", "") in BOT_LOGINS for r in (revs or [])):
            continue
        if not watchdog():
            break
        files_d = gh_pr_files(n)
        patches = ""
        for f in files_d[:5]:
            if f.get("filename", "").endswith((".c", ".h", ".asm")):
                p = f.get("patch", "")[:1500]
                if p:
                    patches += f"\n--- {f.get('filename', '')} ---\n{p}\n"
        prompt = (
            f"Expert code review MaxOS bare metal x86.\n{RULES}\n"
            f"PR #{n}: {title}\nAuteur: {author}\nDiff:\n{patches}\n\n"
            'JSON:\n{"decision":"APPROVE|REQUEST_CHANGES|COMMENT","summary":"2 phrases",'
            '"problems":[],"positives":[],"bare_metal_violations":[],"merge_safe":false}'
        )
        a = _parse_json_robust(ai_call(prompt, max_tokens=2000, timeout=60, tag=f"review/{n}"))
        if not a:
            a = {}
        decision = a.get("decision", "COMMENT")
        merge_safe = a.get("merge_safe", False)
        icon = {"APPROVE": "✅", "REQUEST_CHANGES": "🔴", "COMMENT": "💬"}.get(decision, "💬")
        body = f"## {icon} Code Review MaxOS AI — PR #{n}\n\n{a.get('summary', 'Analyse N/A.')}\n\n"
        if a.get("problems"):
            body += "### ❌ Problèmes\n" + "\n".join(f"- {p}" for p in a["problems"][:6]) + "\n\n"
        if a.get("bare_metal_violations"):
            body += "### ⚠️ Violations\n" + "\n".join(f"- {v}" for v in a["bare_metal_violations"][:5]) + "\n\n"
        if a.get("positives"):
            body += "### ✅ Positifs\n" + "\n".join(f"- {p}" for p in a["positives"][:5]) + "\n\n"
        body += f"\n---\n*MaxOS AI v{VERSION}*"
        if decision == "APPROVE" and merge_safe:
            gh_approve_pr(n, body)
            gh_add_labels(n, ["ai-approved", "ai-reviewed"])
        elif decision == "REQUEST_CHANGES":
            gh_req_changes(n, body)
            gh_add_labels(n, ["ai-rejected", "ai-reviewed"])
        else:
            gh_post_review(n, body, "COMMENT")
            gh_add_labels(n, ["ai-reviewed"])
        disc_log(f"📋 PR #{n} — {decision}", f"**{title[:45]}**", 0x00AAFF)
        reviewed += 1
        time.sleep(1)
    log(f"PRs: {reviewed} reviewée(s)")

def generate_wiki(sources, snap, analyse, history):
    log("=== GÉNÉRATION WIKI/DOCS ===", "WIKI")
    if not watchdog():
        return
    if remaining_time() < 300:
        log("Pas assez de temps pour la wiki", "WARN")
        return

    score = analyse.get("score_actuel", 35)
    features = analyse.get("fonctionnalites_presentes", [])
    missing = analyse.get("fonctionnalites_manquantes_critiques", [])
    stats = proj_stats(sources)
    boot_ok, boot_msg = validate_boot_sector()
    hist_summary = _history_summary(history)
    scores = history.get("score_history", [])

    score_graph = ""
    if len(scores) >= 2:
        max_s = max(scores) or 1
        for s in scores[-10:]:
            bar = "█" * int(s / max_s * 10)
            score_graph += f"`{s:3d}` {bar}\n"

    readme_content = (
        f"# 🖥️ MaxOS — Bare Metal x86 OS\n\n"
        f"> Développé automatiquement par **MaxOS AI v{VERSION}**\n\n"
        f"## 📊 État actuel\n\n"
        f"| Métrique | Valeur |\n|---|---|\n"
        f"| 🎯 Score | **{score}/100** |\n"
        f"| 📈 Niveau | {analyse.get('niveau_os', '?')} |\n"
        f"| 📁 Fichiers | {stats['files']} |\n"
        f"| 📝 Lignes | {stats['lines']:,} |\n"
        f"| 💾 os.img | {'✅ Bootable' if boot_ok else '❌ Non bootable'} |\n"
        f"| 🔐 Boot sector | {boot_msg[:60]} |\n\n"
        f"## 🚀 Lancer MaxOS\n\n"
        f"```bash\n"
        f"# Compiler\nmake\n\n"
        f"# Lancer dans QEMU\n"
        f"qemu-system-i386 -drive format=raw,file=os.img,if=floppy -boot a -vga std -k fr -m 32\n"
        f"```\n\n"
        f"## ✅ Fonctionnalités présentes\n\n"
        + "\n".join(f"- {f}" for f in features) + "\n\n"
        f"## 🚧 En développement\n\n"
        + "\n".join(f"- {f}" for f in missing) + "\n\n"
        f"## 📈 Progression\n\n"
        f"{score_graph}\n"
        f"## 🏗️ Architecture\n\n"
        f"```\nMaxOS/\n├── boot/          # Bootloader NASM\n"
        f"├── kernel/        # Kernel C + ASM\n"
        f"├── drivers/       # Pilotes (screen, keyboard, vga)\n"
        f"├── apps/          # Applications (terminal)\n"
        f"└── ai_dev/        # Bot IA développeur\n```\n\n"
        f"## 🤖 Bot IA\n\n"
        f"{hist_summary}\n\n"
        f"---\n*Mis à jour automatiquement par MaxOS AI v{VERSION}*\n"
    )

    readme_path = os.path.join(REPO_PATH, "README.md")
    try:
        with open(readme_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(readme_content)
        log("README.md mis à jour", "WIKI")
    except Exception as e:
        log(f"Erreur README: {e}", "ERROR")

    arch_sigs = snap.get_all_func_signatures()
    arch_content = (
        f"# Architecture MaxOS\n\n"
        f"## Fonctions canoniques\n\n"
        f"| Fonction | Signature |\n|---|---|\n"
        + "\n".join(f"| `{func}` | `{sig}` |" for func, sig in CANONICAL_SIGNATURES.items())
        + "\n\n"
        f"## Fonctions implémentées ({len(arch_sigs)})\n\n"
        f"| Fonction | Fichier | Signature |\n|---|---|---|\n"
        + "\n".join(
            f"| `{func}` | — | `{sig[:60]}` |"
            for func, sig in list(arch_sigs.items())[:30]
        )
        + "\n\n"
        f"## Règles bare metal\n\n"
        f"```\n{RULES}\n```\n\n"
        f"---\n*MaxOS AI v{VERSION}*\n"
    )

    os.makedirs(os.path.join(REPO_PATH, "docs"), exist_ok=True)
    arch_path = os.path.join(REPO_PATH, "docs", "architecture.md")
    try:
        with open(arch_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(arch_content)
        log("docs/architecture.md généré", "WIKI")
    except Exception as e:
        log(f"Erreur docs/architecture: {e}", "ERROR")

    if not watchdog() or remaining_time() < 200:
        git_cmd(["add", "-A"])
        ok, out, err = git_cmd(["commit", "-m", "docs: update README + architecture [skip ci]"])
        if ok:
            git_cmd(["push", "--set-upstream", "origin", git_current_branch()])
            log("Docs pushés", "WIKI")
        return

    prompt = (
        f"Génère une documentation technique complète pour MaxOS en Markdown.\n"
        f"Score: {score}/100 | Niveau: {analyse.get('niveau_os', '?')}\n"
        f"Features: {', '.join(features[:8])}\n"
        f"Fichiers C: {stats.get('by_ext', {}).get('.c', 0)} | ASM: {stats.get('by_ext', {}).get('.asm', 0)}\n\n"
        "Écris un guide développeur complet (500-800 mots) couvrant:\n"
        "1. Comment compiler\n2. Comment tester dans QEMU\n"
        "3. Structure des fichiers\n4. Comment contribuer\n"
        "5. Roadmap\n"
        "Format Markdown, en français, professionnel."
    )
    wiki_resp = ai_call(prompt, max_tokens=2000, timeout=60, tag="wiki")
    if wiki_resp:
        dev_guide_path = os.path.join(REPO_PATH, "docs", "developer-guide.md")
        try:
            with open(dev_guide_path, "w", encoding="utf-8", newline="\n") as f:
                f.write(f"# Guide Développeur MaxOS\n\n")
                f.write(f"> Généré par MaxOS AI v{VERSION}\n\n")
                f.write(wiki_resp)
                f.write(f"\n\n---\n*MaxOS AI v{VERSION}*\n")
            log("docs/developer-guide.md généré", "WIKI")
        except Exception as e:
            log(f"Erreur developer-guide: {e}", "ERROR")

    git_cmd(["add", "-A"])
    ok, out, err = git_cmd(["commit", "-m", "docs: update wiki + developer guide [skip ci]"])
    if ok:
        git_cmd(["push", "--set-upstream", "origin", git_current_branch()])
        log("Wiki complet pushé", "WIKI")
        disc_log("📖 Wiki mis à jour", "README + architecture + developer-guide", 0x00AAFF)

def create_release(tasks_done, tasks_failed, analyse, stats, history):
    releases = gh_list_releases(10)
    last_tag = "v0.0.0"
    for r in releases:
        tag = r.get("tag_name", "")
        if re.match(r"v\d+\.\d+\.\d+", tag):
            last_tag = tag
            break
    try:
        pts = last_tag.lstrip("v").split(".")
        major, minor, patch = int(pts[0]), int(pts[1]), int(pts[2])
    except:
        major = minor = patch = 0

    score = analyse.get("score_actuel", 35)
    if score >= 80:
        major += 1
        minor = 0
        patch = 0
    elif score >= 60:
        minor += 1
        patch = 0
    else:
        patch += 1
    new_tag = f"v{major}.{minor}.{patch}"

    img_path = os.path.join(REPO_PATH, "os.img")
    img_ok = os.path.exists(img_path) and os.path.getsize(img_path) > 512
    img_size = os.path.getsize(img_path) if img_ok else 0
    boot_ok, boot_msg = validate_boot_sector()
    qemu_ok, qemu_msg = run_qemu_test()

    compare = gh_compare(last_tag, "HEAD")
    commits = compare.get("commits", [])
    ahead_by = compare.get("ahead_by", len(commits))
    chg_lines = []
    for c in commits[:20]:
        sha = c.get("sha", "")[:7]
        msg = c.get("commit", {}).get("message", "").split("\n")[0][:80]
        if msg and not msg.startswith("[skip"):
            chg_lines.append(f"- `{sha}` {msg}")
    changelog = "\n".join(chg_lines) or "- Maintenance"

    changes_ok = "".join(
        f"- ✅ **{t.get('nom', '?')[:50]}** [`{t.get('sha', '?')[:7]}`]"
        f"{' (fix×' + str(t['fix_count']) + ')' if t.get('fix_count', 0) > 0 else ''} — {t.get('elapsed', 0):.0f}s"
        f"{' 💻' if t.get('qemu_ok') else ''}\n"
        for t in tasks_done
    )
    changes_fail = (
        "\n## ⏭️ Reporté\n\n" + "\n".join(f"- ❌ {n}" for n in tasks_failed) + "\n"
        if tasks_failed else ""
    )

    tk = sum(p["tokens"] for p in PROVIDERS)
    now = datetime.utcnow()
    prov_table = ""
    for p in sorted(PROVIDERS, key=lambda x: -x["calls"]):
        if p["calls"] == 0:
            continue
        st = "💀" if p["dead"] else "🟢"
        prov_table += f"| {st} `{p['id']}` | {p['calls']} | ~{p['tokens']:,} | {avg_rt(p):.1f}s |\n"

    scores = history.get("score_history", [])
    score_trend = "stable"
    if len(scores) >= 3:
        if scores[-1] > scores[-3]:
            score_trend = "↗️ hausse"
        elif scores[-1] < scores[-3]:
            score_trend = "↘️ baisse"

    body = (
        f"# 🖥️ MaxOS {new_tag}\n\n> 🤖 Généré par **MaxOS AI v{VERSION}**\n\n---\n\n"
        f"## 📊 État\n\n| Métrique | Valeur |\n|---|---|\n"
        f"| 🎯 Score | **{score}/100** ({score_trend}) |\n"
        f"| 📈 Niveau | {analyse.get('niveau_os', '?')} |\n"
        f"| 📁 Fichiers | {stats.get('files', 0)} |\n"
        f"| 📝 Lignes | {stats.get('lines', 0):,} |\n"
        f"| 💾 os.img | {'✅ ' + str(img_size) + ' bytes' if img_ok else '❌ non généré'} |\n"
        f"| 🔐 Boot | {boot_msg[:60]} |\n"
        f"| 💻 QEMU | {'✅ ' + qemu_msg[:40] if qemu_ok else ('⚠️ Non testé' if qemu_ok is None else '❌ ' + qemu_msg[:40])} |\n"
        f"| 🔄 Cycles | {history.get('cycle_count', 0)} |\n\n"
        f"## ✅ Améliorations ({len(tasks_done)})\n\n{changes_ok or '*(aucune)*'}"
        f"{changes_fail}\n"
        f"## 🚀 Tester MaxOS\n\n```bash\n"
        f"# Compiler\nmake\n\n"
        f"# Lancer dans QEMU\n"
        f"qemu-system-i386 -drive format=raw,file=os.img,if=floppy -boot a -vga std -k fr -m 32\n"
        f"```\n\n"
        f"## 📝 Changelog {last_tag} → {new_tag} ({ahead_by} commits)\n\n{changelog}\n\n"
        f"## 🤖 Stats IA\n\n| Métrique | Valeur |\n|---|---|\n"
        f"| Appels IA | {_CYCLE_STATS.get('ai_calls', 0)} |\n"
        f"| 429 total | {_CYCLE_STATS.get('total_429', 0)} |\n"
        f"| Tokens | ~{tk:,} |\n"
        f"| Builds OK | {_CYCLE_STATS.get('builds_ok', 0)} |\n"
        f"| Auto-fix OK | {_CYCLE_STATS.get('auto_fix_success', 0)} |\n\n"
        f"### Providers\n\n| Status | ID | Appels | Tokens | Avg RT |\n|---|---|---|---|---|\n"
        f"{prov_table or '*(aucun)*'}\n\n"
        f"---\n*MaxOS AI v{VERSION} | {now.strftime('%Y-%m-%d %H:%M')} UTC*\n"
    )

    pre = score < 50
    release_data = gh_create_release(
        new_tag,
        f"MaxOS {new_tag} — {analyse.get('niveau_os', '?')} — {now.strftime('%Y-%m-%d')}",
        body, pre=pre
    )

    if release_data:
        release_id = release_data.get("id")
        release_url = release_data.get("html_url", "?")
        log(f"Release {new_tag} créée: {release_url}", "OK")
        if img_ok and release_id:
            asset_url = gh_upload_asset(release_id, img_path, "os.img")
            if asset_url:
                log(f"os.img uploadé: {asset_url}", "OK")
        disc_now(f"🚀 Release {new_tag} !",
                 f"Score: **{score}/100** ({score_trend}) | QEMU: {'✅' if qemu_ok else '⚠️'}",
                 0x00FF88 if not pre else 0xFFA500,
                 [{"name": "🏷️ Version", "value": new_tag, "inline": True},
                  {"name": "📊 Score", "value": f"{score}/100", "inline": True},
                  {"name": "💾 os.img", "value": "✅ Bootable" if img_ok else "❌ Manquant", "inline": True},
                  {"name": "🔐 Boot", "value": boot_msg[:60], "inline": True},
                  {"name": "💻 QEMU", "value": qemu_msg[:50] if qemu_ok is not None else "Non testé", "inline": True},
                  {"name": "🔗 Lien", "value": f"[Release]({release_url})", "inline": False}])
    else:
        log("Release: échec", "ERROR")
    return release_data

def final_report(success, total, tasks_done, tasks_failed, analyse, stats, history):
    score = analyse.get("score_actuel", 35)
    pct = int(success / total * 100) if total > 0 else 0
    color = 0x00FF88 if pct >= 80 else 0xFFA500 if pct >= 50 else 0xFF4444
    elapsed = int(time.time() - START_TIME)
    tk = sum(p["tokens"] for p in PROVIDERS)
    img_ok = os.path.exists(os.path.join(REPO_PATH, "os.img"))
    sources = read_all()
    qual = analyze_quality(sources)
    boot_ok, boot_msg = validate_boot_sector()
    qemu_ok, qemu_msg = run_qemu_test()
    done_s = "\n".join(
        f"✅ {t.get('nom', '?')[:42]} ({t.get('elapsed', 0):.0f}s)"
        + (f" fix×{t['fix_count']}" if t.get("fix_count", 0) > 0 else "")
        + (" 💻" if t.get("qemu_ok") else "")
        for t in tasks_done
    ) or "Aucune"
    fail_s = "\n".join(f"❌ {n[:42]}" for n in tasks_failed) or "Aucune"
    disc_now(f"🏁 Cycle #{history.get('cycle_count', 0)} — {success}/{total}",
             f"```\n{pbar(pct)}\n```\n**{pct}%** | os.img: {'✅' if img_ok else '❌'} | QEMU: {'✅' if qemu_ok else '⚠️'}",
             color,
             [{"name": "✅", "value": str(success), "inline": True},
              {"name": "❌", "value": str(total - success), "inline": True},
              {"name": "⏱️", "value": f"{elapsed}s", "inline": True},
              {"name": "💬 Tokens", "value": f"{tk:,}", "inline": True},
              {"name": "📊 Qualité", "value": f"{qual['score']}/100", "inline": True},
              {"name": "💾 os.img", "value": "✅ OK" if img_ok else "❌ Manquant", "inline": True},
              {"name": "🔐 Boot", "value": boot_msg[:60], "inline": True},
              {"name": "💻 QEMU", "value": qemu_msg[:50] if qemu_ok is not None else "Non testé", "inline": True},
              {"name": "✅ Réussies", "value": done_s[:900], "inline": False},
              {"name": "❌ Échouées", "value": fail_s[:500], "inline": False},
              {"name": "🔑 Providers", "value": prov_summary()[:600], "inline": False}])

    if success == 0 and total > 0:
        history_cycles = history.get("cycles", [])
        consecutive_zero = sum(1 for c in history_cycles[-3:] if c.get("success", 0) == 0)
        if consecutive_zero >= 3:
            disc_now("🚨 ALERTE: 3 cycles 0 succès",
                     "Le projet est bloqué. Intervention manuelle recommandée.",
                     0xFF0000,
                     [{"name": "Action", "value": "Vérifier le Makefile et les erreurs de build", "inline": False}])

def main():
    print("=" * 64)
    print(f"  MaxOS AI Developer v{VERSION}")
    print(f"  Architecture: Snapshot | Knowledge Base | QEMU | Wiki | History")
    print("=" * 64)
    if not PROVIDERS:
        print("FATAL: Aucun provider IA.")
        sys.exit(1)

    by_type = defaultdict(list)
    for p in PROVIDERS:
        by_type[p["type"]].append(p)
    for t in sorted(by_type.keys()):
        ps = by_type[t]
        ku = len(set(p["key"][:8] for p in ps))
        mu = len(set(p["model"] for p in ps))
        print(f"  {t:12s}: {ku} clé(s) × {mu} modèle(s) = {len(ps)} providers | spé: {PROVIDER_SPECIALIZATION.get(t, [])}")
    print(f"  {'TOTAL':12s}: {len(PROVIDERS)} providers")
    print(f"  {'RUNTIME':12s}: {MAX_RUNTIME}s max | DEBUG: {'ON' if DEBUG else 'OFF'}")
    print("=" * 64 + "\n")

    history = _load_history()
    blacklist = _load_blacklist()
    log(f"Historique: {history.get('cycle_count', 0)} cycles | Blacklist: {len(blacklist)} tâches", "HIST")

    disc_now(f"🤖 MaxOS AI v{VERSION} — Démarrage",
             f"`{len(PROVIDERS)}` providers | Cycle #{history.get('cycle_count', 0) + 1}", 0x5865F2,
             [{"name": "🔑 Providers", "value": prov_summary()[:800], "inline": False},
              {"name": "📁 Repo", "value": f"`{REPO_OWNER}/{REPO_NAME}`", "inline": True},
              {"name": "⏱️ Runtime", "value": f"{MAX_RUNTIME}s max", "inline": True},
              {"name": "📚 Historique", "value": _history_summary(history)[:300], "inline": False}])

    subprocess.run(["make", "clean"], cwd=REPO_PATH, capture_output=True, timeout=30)
    log("Setup: labels GitHub...")
    gh_ensure_labels(STANDARD_LABELS)
    ms_cache = {}

    log("[Issues] Traitement...")
    ms_cache = handle_issues(ms_cache) or ms_cache
    if not watchdog():
        sys.exit(0)
    log("[Stale] Vérification...")
    handle_stale()
    if not watchdog():
        sys.exit(0)
    log("[PRs] Traitement...")
    handle_prs()
    if not watchdog():
        sys.exit(0)

    log("[Pre-flight] Build initial...")
    pf_ok, pf_errs = pre_flight_check()

    sources = read_all(force=True)
    stats = proj_stats(sources)
    qual = analyze_quality(sources)
    snap = ProjectSnapshot(sources)

    log(f"Sources: {stats['files']} fichiers | {stats['lines']:,} lignes")
    log(f"Qualité: {qual['score']}/100 | {len(qual['violations'])} violation(s)")

    consistency = snap.check_consistency()
    if consistency:
        log(f"Cohérence: {len(consistency)} problème(s) détecté(s)", "WARN")
        for issue in consistency:
            log(f"  {issue}", "WARN")

    boot_ok, boot_msg = validate_boot_sector()
    log(f"Boot sector: {boot_msg}", "OK" if boot_ok else "WARN")

    disc_now("📊 Sources",
             f"`{stats['files']}` fichiers | `{stats['lines']:,}` lignes", 0x5865F2,
             [{"name": "Qualité", "value": f"{qual['score']}/100", "inline": True},
              {"name": "C", "value": f"{qual['c_files']} .c/.h", "inline": True},
              {"name": "ASM", "value": f"{qual['asm_files']} .asm", "inline": True},
              {"name": "🔐 Boot", "value": boot_msg[:80], "inline": False},
              {"name": "⚠️ Cohérence", "value": "\n".join(consistency[:5]) or "✅ OK", "inline": False}])

    analyse = phase_analyse(build_ctx(sources), stats, snap, history)
    score = analyse.get("score_actuel", 35)
    niveau = analyse.get("niveau_os", "?")
    plan = analyse.get("plan_ameliorations", [])
    milestone = analyse.get("prochaine_milestone", "?")
    features = analyse.get("fonctionnalites_presentes", [])
    manques = analyse.get("fonctionnalites_manquantes_critiques", [])

    order = {"CRITIQUE": 0, "HAUTE": 1, "NORMALE": 2, "BASSE": 3, "ELEVEE": 1, "FAIBLE": 3}
    plan = sorted(plan, key=lambda t: (order.get(t.get("priorite", "NORMALE"), 2), t.get("nom", "")))

    plan_filtered = []
    skipped_bl = []
    for t in plan:
        tname = t.get("nom", "?")
        if _check_blacklist(blacklist, tname):
            skipped_bl.append(tname)
            log(f"Blacklisté (3 échecs consécutifs): {tname}", "WARN")
        else:
            plan_filtered.append(t)
    if skipped_bl:
        disc_log("🚫 Blacklist", "\n".join(f"`{n[:50]}`" for n in skipped_bl[:5]), 0xFF6600)
    plan = plan_filtered

    log(f"Score={score}/100 | {niveau} | {len(plan)} tâche(s) | {len(skipped_bl)} blacklistées", "STAT")

    if milestone and milestone not in ms_cache:
        ms_num = gh_ensure_milestone(milestone, f"Objectif: {milestone}")
        if ms_num:
            ms_cache[milestone] = ms_num

    disc_now(f"📊 Analyse: {score}/100",
             f"```\n{pbar(score)}\n```",
             0x00AAFF if score >= 60 else 0xFFA500 if score >= 30 else 0xFF4444,
             [{"name": "✅ Présentes", "value": "\n".join(f"+ {f}" for f in features[:6]) or "—", "inline": True},
              {"name": "❌ Manquantes", "value": "\n".join(f"- {f}" for f in manques[:6]) or "—", "inline": True},
              {"name": "📋 Plan", "value": "\n".join(
                  f"[{i + 1}] `{t.get('priorite', '?')[:3]}` {t.get('nom', '?')[:38]}"
                  for i, t in enumerate(plan[:8])) or "—", "inline": False},
              {"name": "🎯 Milestone", "value": milestone[:80], "inline": True}])

    log("[Issues auto] Création issues détectées...")
    create_bot_issues(sources, snap, analyse)

    total = len(plan)
    success = 0
    tasks_done = []
    tasks_failed = []

    for i, task in enumerate(plan, 1):
        if not watchdog():
            log(f"Watchdog: arrêt avant tâche {i}/{total}", "WARN")
            break
        if remaining_time() < 200:
            log("Moins de 200s restantes — arrêt", "WARN")
            break

        disc_log(f"💓 [{i}/{total}] {task.get('nom', '?')[:45]}",
                 f"Uptime: {uptime()} | Reste: {int(remaining_time())}s\n{prov_summary()[:250]}",
                 0x7289DA)

        sources_now = read_all()
        snap_now = ProjectSnapshot(sources_now)

        ok, written, deleted, metrics = implement(task, sources_now, snap_now, i, total)
        TASK_METRICS.append(metrics)
        tname = task.get("nom", "?")
        blacklist = _update_blacklist(blacklist, tname, ok)

        if ok:
            success += 1
            tasks_done.append(metrics)
        else:
            tasks_failed.append(tname)

        if i < total and watchdog():
            n_al = len(alive())
            pause = 3 if n_al >= 5 else 6 if n_al >= 3 else 12 if n_al >= 1 else 20
            log(f"Pause {pause}s ({n_al} dispo, {int(remaining_time())}s restants)")
            _flush_disc(True)
            time.sleep(pause)

    _save_blacklist(blacklist)

    log(f"\n{'=' * 56}\nCYCLE TERMINÉ: {success}/{total}\n{'=' * 56}")

    ensure_osimg()

    sf = read_all(force=True)
    snap_final = ProjectSnapshot(sf)

    if watchdog() and remaining_time() > 150:
        log("[Wiki] Génération docs...")
        generate_wiki(sf, snap_final, analyse, history)

    if success > 0:
        log("[Release] Création...")
        create_release(tasks_done, tasks_failed, analyse, proj_stats(sf), history)
    else:
        log("[Release] 0 succès — pas de release")

    history = _update_history(history, {
        "score": score,
        "success": success,
        "total": total,
        "img_ok": os.path.exists(os.path.join(REPO_PATH, "os.img")),
        "tasks_done": tasks_done,
        "tasks_failed": tasks_failed,
    })
    _save_history(history)

    final_report(success, total, tasks_done, tasks_failed, analyse, proj_stats(sf), history)
    _flush_disc(True)

    print(f"\n{'=' * 64}")
    img_ok = os.path.exists(os.path.join(REPO_PATH, "os.img"))
    img_size = os.path.getsize(os.path.join(REPO_PATH, "os.img")) if img_ok else 0
    boot_ok, boot_msg = validate_boot_sector()
    print(f"[FIN] {success}/{total} | uptime: {uptime()} | GH RL: {GH_RATE['remaining']}")
    print(f"      os.img: {'✅ ' + str(img_size) + ' bytes' if img_ok else '❌ MANQUANT'}")
    print(f"      boot: {boot_msg[:60]}")
    print(f"      IA calls: {_CYCLE_STATS.get('ai_calls', 0)} | 429: {_CYCLE_STATS.get('total_429', 0)}")
    print(f"      Cycle #{history.get('cycle_count', 0)} | Blacklist: {len(blacklist)}")
    for t in tasks_done:
        fc = t.get("fix_count", 0)
        print(f"  ✅ {t.get('nom', '?')[:58]} ({t.get('elapsed', 0):.0f}s){' fix×' + str(fc) if fc else ''}")
    for n in tasks_failed:
        print(f"  ❌ {n[:58]}")
    print("=" * 64)

if __name__ == "__main__":
    main()
