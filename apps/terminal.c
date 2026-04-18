#include "terminal.h"
#include "../drivers/screen.h"
#include "../ui/ui.h"
#include "../drivers/keyboard.h" /* Pour KEY_UP, KEY_DOWN, etc. */

#define TM_LINES  13
#define TM_W      76
#define TM_ROW    (WIN_R + 2)
#define TM_TH     (WIN_H - 5)

#define HISTORY_SIZE 16
#define MAX_CMD_LEN TM_W

static char tm_buf[TM_LINES][TM_W];
static int  tm_cur = 0;
static char tm_in[MAX_CMD_LEN];
static int  tm_ic  = 0;

/* Historique des commandes */
static char tm_history[HISTORY_SIZE][MAX_CMD_LEN];
static int  tm_history_count = 0;
static int  tm_history_idx = 0;

/* Complétion automatique */
static const char* commands[] = {
    "help", "clear", "uname", "mem", "cpu", "ls", "date", "version", "echo",
    /* Ajoutez d'autres commandes ici si nécessaire */
};
static int num_commands = sizeof(commands) / sizeof(commands[0]);

/* ── utils ── */
static int se(const char* a, const char* b) {
    int i = 0;
    while (a[i] && b[i] && a[i] == b[i]) i++;
    return a[i] == b[i];
}

static int starts_with(const char* str, const char* prefix) {
    while (*prefix) {
        if (*str != *prefix) return 0;
        str++;
        prefix++;
    }
    return 1;
}

static void sc(char* d, const char* s, int max) {
    int i = 0;
    while (s[i] && i < max - 1) { d[i] = s[i]; i++; }
    d[i] = '\0';
}

static void mc(char* b, int n) {
    int i; for (i = 0; i < n; i++) b[i] = '\0';
}

static void scroll(void) {
    int i;
    for (i = 0; i < TM_LINES - 1; i++)
        sc(tm_buf[i], tm_buf[i + 1], TM_W);
    mc(tm_buf[TM_LINES - 1], TM_W);
    if (tm_cur > 0) tm_cur--;
}

static void println(const char* s) {
    if (tm_cur >= TM_LINES) scroll();
    sc(tm_buf[tm_cur], s, TM_W);
    tm_cur++;
}

static void add_to_history(const char* cmd) {
    if (cmd[0] == '\0') return;
    if (tm_history_count < HISTORY_SIZE) {
        sc(tm_history[tm_history_count], cmd, MAX_CMD_LEN);
        tm_history_count++;
    } else {
        /* Décaler l'historique pour faire de la place */
        int i;
        for (i = 0; i < HISTORY_SIZE - 1; i++) {
            sc(tm_history[i], tm_history[i + 1], MAX_CMD_LEN);
        }
        sc(tm_history[HISTORY_SIZE - 1], cmd, MAX_CMD_LEN);
    }
    tm_history_idx = tm_history_count; /* Réinitialiser l'index pour la navigation */
}

static void get_history_entry(int direction) {
    if (tm_history_count == 0) return;

    if (direction == KEY_UP) {
        if (tm_history_idx > 0) tm_history_idx--;
    } else if (direction == KEY_DOWN) {
        if (tm_history_idx < tm_history_count - 1) tm_history_idx++;
        else tm_history_idx = tm_history_count; /* Retour au prompt vide */
    }

    if (tm_history_idx < tm_history_count) {
        sc(tm_in, tm_history[tm_history_idx], MAX_CMD_LEN);
        tm_ic = 0;
        while (tm_in[tm_ic] != '\0') tm_ic++;
    } else {
        mc(tm_in, MAX_CMD_LEN);
        tm_ic = 0;
    }
}

static void complete_command(void) {
    if (tm_ic == 0) return;

    char current_prefix[MAX_CMD_LEN];
    sc(current_prefix, tm_in, MAX_CMD_LEN);

    const char* best_match = 0;
    int match_count = 0;

    for (int i = 0; i < num_commands; i++) {
        if (starts_with(commands[i], current_prefix)) {
            if (best_match == 0) {
                best_match = commands[i];
            }
            match_count++;
        }
    }

    if (best_match) {
        if (match_count == 1) {
            /* Complétion unique, on remplace le buffer */
            sc(tm_in, best_match, MAX_CMD_LEN);
            tm_ic = 0;
            while (tm_in[tm_ic] != '\0') tm_ic++;
        } else {
            /* Plusieurs correspondances, afficher la liste */
            println(""); /* Ligne vide pour l'espacement */
            char line[TM_W];
            int line_idx = 0;
            line[line_idx++] = ' ';
            line[line_idx++] = ' ';
            for (int i = 0; i < num_commands; i++) {
                if (starts_with(commands[i], current_prefix)) {
                    int cmd_len = 0;
                    while (commands[i][cmd_len] != '\0') cmd_len++;
                    if (line_idx + cmd_len + 1 < TM_W) {
                        sc(line + line_idx, commands[i], TM_W - line_idx);
                        line_idx += cmd_len;
                        line[line_idx++] = ' ';
                    } else {
                        break; /* Pas assez de place sur la ligne */
                    }
                }
            }
            line[line_idx] = '\0';
            println(line);
        }
    }
}


void tm_init(void) {
    int i;
    for (i = 0; i < TM_LINES; i++) mc(tm_buf[i], TM_W);
    tm_cur = 0;
    mc(tm_in, MAX_CMD_LEN);
    tm_ic = 0;
    tm_history_count = 0;
    tm_history_idx = 0;

    println("MaxOS Terminal v1.1");
    println("Tape 'help' pour la liste des commandes.");
    println("------------------------------------------");
}

/* Horloge externe */
extern unsigned int CLK_H;
extern unsigned int CLK_M;
extern unsigned int CLK_S;

static void exec(const char* cmd) {
    /* Afficher prompt + commande */
    char line[TM_W];
    int i = 0;
    line[i++] = '$'; line[i++] = ' ';
    int j = 0;
    while (cmd[j] && i < TM_W - 1) line[i++] = cmd[j++];
    line[i] = '\0';
    println(line);

    if (cmd[0] == '\0') {
        /* Rien à exécuter */
    } else if (se(cmd, "help")) {
        println("  help     - Cette aide");
        println("  clear    - Vider le terminal");
        println("  uname    - Infos systeme");
        println("  mem      - Infos memoire");
        println("  cpu      - Infos CPU");
        println("  ls       - Lister fichiers");
        println("  date     - Date et heure");
        println("  version  - Version MaxOS");
        println("  echo [x] - Afficher texte");
        println("  tab      - Complétion automatique");
        println("  up/down  - Historique commandes");
    } else if (se(cmd, "clear")) {
        int k; for (k = 0; k < TM_LINES; k++) mc(tm_buf[k], TM_W);
        tm_cur = 0;
    } else if (se(cmd, "uname")) {
        println("  MaxOS 1.1 x86 32-bit Protected Mode");
        println("  Noyau : C + NASM  |  Build 2024");
    } else if (se(cmd, "mem")) {
        println("  RAM basse   : 640 KB");
        println("  RAM haute   : ~255 MB");
        println("  Kernel      : 0x8000");
        println("  VGA         : 0xB8000");
        println("  Stack       : 0x90000");
    } else if (se(cmd, "cpu")) {
        println("  Arch    : x86 Intel/AMD");
        println("  Mode    : Protected 32-bit");
        println("  GDT     : Active");
    } else if (se(cmd, "ls")) {
        println("  boot.bin       512 B");
        println("  kernel.bin    8192 B");
        println("  notes.txt     1024 B");
        println("  readme.txt     256 B");
    } else if (se(cmd, "date")) {
        char d[32];
        d[0] = ' '; d[1] = 'H'; d[2] = 'e'; d[3] = 'u';
        d[4] = 'r'; d[5] = 'e'; d[6] = ':'; d[7] = ' ';
        d[8] = (char)('0' + CLK_H / 10); d[9] = (char)('0' + CLK_H % 10);
        d[10] = ':';
        d[11] = (char)('0' + CLK_M / 10); d[12] = (char)('0' + CLK_M % 10);
        d[13] = ':';
        d[14] = (char)('0' + CLK_S / 10); d[15] = (char)('0' + CLK_S % 10);
        d[16] = '\0';
        println(d);
    } else if (se(cmd, "version")) {
        println("  MaxOS v1.1");
        println("  x86 32-bit | VGA 80x25 | PS/2 AZERTY");
    } else if (starts_with(cmd, "echo ")) {
        char out[TM_W];
        out[0] = ' '; out[1] = ' ';
        int oi = 2, ci = 5;
        while (cmd[ci] && oi < TM_W - 1) out[oi++] = cmd[ci++];
        out[oi] = '\0';
        println(out);
    } else {
        println("  Commande inconnue. Tape 'help'.");
    }
}

void tm_draw(void) {
    v_window(WIN_R, WIN_C, WIN_H, WIN_W, "Terminal - MaxOS", 1);

    /* Menu */
    const char* menu[] = { "Shell", "Options", "Aide" };
    v_menubar(WIN_R + 1, WIN_C, WIN_W, menu, 3);

    /* Zone noire */
    int tz = WIN_R + 2;
    int th = WIN_H - 4;
    v_fill(tz, WIN_C, th, WIN_W, C_WHITE, C_BLACK);

    /* Lignes */
    int i;
    for (i = 0; i < th && i < TM_LINES; i++) {
        v_fill(tz + i, WIN_C + 1, 1, WIN_W - 2, C_WHITE, C_BLACK);
        if (tm_buf[i][0]) {
            int fg;
            if (tm_buf[i][0] == '$')      fg = C_LGREEN;
            else if (tm_buf[i][0] == '-') fg = C_DGREY;
            else if (tm_buf[i][0] == ' ') fg = C_GREEN;
            else                          fg = C_CYAN;
            v_str(tz + i, WIN_C + 1, tm_buf[i], fg, C_BLACK);
        }
    }

    /* Ligne input */
    int ir = tz + th - 1;
    v_fill(ir, WIN_C, 1, WIN_W, C_LGREEN, C_BLACK);
    v_str(ir, WIN_C + 1, "root@maxos:~$ ", C_LGREEN, C_BLACK);
    for (i = 0; i < tm_ic && i < WIN_W - 16; i++)
        v_put(ir, WIN_C + 15 + i, tm_in[i], C_WHITE, C_BLACK);
    v_put(ir, WIN_C + 15 + tm_ic, '_', C_LGREEN, C_BLACK);

    /* Status */
    v_statusbar(WIN_R + WIN_H - 1, WIN_C, WIN_W,
                "bash | root@maxos | ~", "MaxOS 1.1");
}

void tm_key(char k) {
    if (k == KEY_NULL) return;

    if (k == KEY_BACKSPACE) {
        if (tm_ic > 0) { tm_ic--; tm_in[tm_ic] = '\0'; }
    } else if (k == KEY_ENTER) {
        tm_in[tm_ic] = '\0';
        add_to_history(tm_in);
        exec(tm_in);
        mc(tm_in, MAX_CMD_LEN);
        tm_ic = 0;
    } else if (k == KEY_UP || k == KEY_DOWN) {
        get_history_entry(k);
    } else if (k == KEY_TAB) {
        complete_command();
    } else if (k >= 0x20 && (unsigned char)k < 0x7F) {
        if (tm_ic < MAX_CMD_LEN - 2) { /* -2 pour laisser place au '\0' et au curseur */
            tm_in[tm_ic] = k;
            tm_ic++;
        }
    }
    tm_draw();
}