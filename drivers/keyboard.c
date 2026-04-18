#include "keyboard.h"

static unsigned char inb(unsigned short port) {
    unsigned char v;
    __asm__ volatile("inb %1,%0" : "=a"(v) : "dN"(port));
    return v;
}

/* AZERTY Scancode Set 1 */
static const char SC_NORMAL[58] = {
    0,       /* 00 */
    0x1B,    /* 01 ESC */
    '&',     /* 02 */
    '\xE9',  /* 03 é -> on va le remplacer par 2 */
    '"',     /* 04 */
    '\'',    /* 05 */
    '(',     /* 06 */
    '-',     /* 07 */
    '\xE8',  /* 08 è */
    '_',     /* 09 */
    '\xE7',  /* 0A ç */
    '\xE0',  /* 0B à */
    ')',     /* 0C */
    '=',     /* 0D */
    0x08,    /* 0E BACKSPACE */
    0x09,    /* 0F TAB */
    'a',     /* 10 */
    'z',     /* 11 */
    'e',     /* 12 */
    'r',     /* 13 */
    't',     /* 14 */
    'y',     /* 15 */
    'u',     /* 16 */
    'i',     /* 17 */
    'o',     /* 18 */
    'p',     /* 19 */
    '^',     /* 1A */
    '$',     /* 1B */
    0x0A,    /* 1C ENTER */
    0,       /* 1D CTRL */
    'q',     /* 1E */
    's',     /* 1F */
    'd',     /* 20 */
    'f',     /* 21 */
    'g',     /* 22 */
    'h',     /* 23 */
    'j',     /* 24 */
    'k',     /* 25 */
    'l',     /* 26 */
    'm',     /* 27 */
    '%',     /* 28 */
    0,       /* 29 */
    0,       /* 2A LSHIFT */
    '*',     /* 2B */
    'w',     /* 2C */
    'x',     /* 2D */
    'c',     /* 2E */
    'v',     /* 2F */
    'b',     /* 30 */
    'n',     /* 31 */
    ',',     /* 32 */
    ';',     /* 33 */
    ':',     /* 34 */
    '!',     /* 35 */
    0,       /* 36 RSHIFT */
    '*',     /* 37 */
    0,       /* 38 ALT */
    ' '      /* 39 ESPACE */
};

static const char SC_SHIFT[58] = {
    0,    0x1B,
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
    ')', '+',
    0x08, 0x09,
    'A','Z','E','R','T','Y','U','I','O','P',
    '^','$',
    0x0A,
    0,
    'Q','S','D','F','G','H','J','K','L','M',
    '%', 0,
    0,
    '*',
    'W','X','C','V','B','N',
    '?','.','/','+',
    0,'*',0,' '
};

static int g_shift = 0;
static int g_caps  = 0;
static int g_ext   = 0;

void kb_init(void) {
    g_shift = 0; g_caps = 0; g_ext = 0;
    while (inb(0x64) & 1) inb(0x60);
}

int kb_haskey(void) {
    return inb(0x64) & 1;
}

char kb_getchar(void) {
    unsigned char sc = inb(0x60);

    if (sc == 0xE0) { g_ext = 1; return KEY_NULL; }

    /* Relâchement */
    if (sc & 0x80) {
        unsigned char r = sc & 0x7F;
        if (r == 0x2A || r == 0x36) g_shift = 0;
        g_ext = 0;
        return KEY_NULL;
    }

    /* Touches étendues */
    if (g_ext) {
        g_ext = 0;
        switch (sc) {
            case 0x48: return KEY_UP;
            case 0x50: return KEY_DOWN;
            case 0x4B: return KEY_LEFT;
            case 0x4D: return KEY_RIGHT;
            case 0x47: return KEY_HOME;
            case 0x4F: return KEY_END;
            case 0x53: return KEY_DELETE;
            default:   return KEY_NULL;
        }
    }

    /* Modificateurs */
    if (sc == 0x2A || sc == 0x36) { g_shift = 1; return KEY_NULL; }
    if (sc == 0x3A) { g_caps = !g_caps;           return KEY_NULL; }
    if (sc == 0x1D || sc == 0x38)                 return KEY_NULL;

    /* ═══════════════════════════════════
       TOUCHES DE FONCTION
       On les retourne DIRECTEMENT
       sans passer par les tables
    ═══════════════════════════════════ */
    switch (sc) {
        case 0x3B: return KEY_F1;
        case 0x3C: return KEY_F2;
        case 0x3D: return KEY_F3;
        case 0x3E: return KEY_F4;
        case 0x3F: return KEY_F5;
        case 0x40: return KEY_F6;
        /* Flèches sans E0 */
        case 0x48: return KEY_UP;
        case 0x50: return KEY_DOWN;
        case 0x4B: return KEY_LEFT;
        case 0x4D: return KEY_RIGHT;
        case 0x47: return KEY_HOME;
        case 0x4F: return KEY_END;
        case 0x53: return KEY_DELETE;
    }

    if (sc >= 58) return KEY_NULL;

    char c = g_shift ? SC_SHIFT[sc] : SC_NORMAL[sc];

    /* CAPS LOCK */
    if (g_caps) {
        if (c >= 'a' && c <= 'z') c = (char)(c - 32);
        else if (c >= 'A' && c <= 'Z') c = (char)(c + 32);
    }

    return c ? c : KEY_NULL;
}