#include "notepad.h"
#include "../drivers/screen.h"
#include "../ui/ui.h"

#define NP_ROWS   17
#define NP_COLS   72

/* Zone de texte */
#define NP_TR  (WIN_R + 3)    /* text area row start */
#define NP_TC  (WIN_C + 5)    /* text area col start */
#define NP_TH  (WIN_H - 5)    /* text area height    */
#define NP_TW  (WIN_W - 7)    /* text area width     */

static char buf[NP_ROWS][NP_COLS];
static int  cur_r = 0;
static int  cur_c = 0;
static int  dirty = 0;

void np_init(void) {
    int r, c;
    for (r = 0; r < NP_ROWS; r++)
        for (c = 0; c < NP_COLS; c++)
            buf[r][c] = '\0';
    cur_r = 0; cur_c = 0; dirty = 0;
}

static int row_len(int r) {
    int c = 0;
    while (c < NP_COLS - 1 && buf[r][c]) c++;
    return c;
}

void np_draw(void) {
    /* Cadre fenêtre */
    v_window(WIN_R, WIN_C, WIN_H, WIN_W, "Bloc-Notes - Sans titre", 1);

    /* Menu bar */
    const char* menu[] = {
        "Fichier", "Edition", "Format", "Affichage", "Aide"
    };
    v_menubar(WIN_R + 1, WIN_C, WIN_W, menu, 5);

    /* Règle */
    v_fill(WIN_R + 2, WIN_C, 1, WIN_W, C_DGREY, C_LGREY);
    v_str(WIN_R + 2, WIN_C + 5,
        "1    |    2    |    3    |    4    |    5    |    6    |    7",
        C_DGREY, C_LGREY);

    /* Numéros de ligne + fond texte */
    int r;
    for (r = 0; r < NP_TH && r < NP_ROWS; r++) {
        int tr = NP_TR + r;
        int is_cur = (r == cur_r);

        /* Numéro de ligne */
        v_fill(tr, WIN_C, 1, 4, C_DGREY, C_LGREY);
        v_int(tr, WIN_C + 1, r + 1, C_DGREY, C_LGREY);
        v_put(tr, WIN_C + 4, '|', C_LGREY, C_WHITE);

        /* Ligne de texte */
        int lbg = is_cur ? C_LGREY : C_WHITE;
        v_fill(tr, NP_TC, 1, NP_TW, C_BLACK, lbg);

        /* Caractères */
        int c;
        int len = row_len(r);
        for (c = 0; c < len && c < NP_TW; c++) {
            v_put(tr, NP_TC + c, buf[r][c], C_BLACK, lbg);
        }

        /* Scrollbar */
        v_put(tr, WIN_C + WIN_W - 1, '|', C_LGREY, C_LGREY);
    }

    /* Curseur (bloc bleu) */
    if (cur_r < NP_TH) {
        char cch = buf[cur_r][cur_c];
        if (!cch) cch = ' ';
        v_put(NP_TR + cur_r, NP_TC + cur_c, cch, C_WHITE, C_BLUE);
    }

    /* Scrollbar décorative */
    v_vl(NP_TR, WIN_C + WIN_W - 1, NP_TH, '|', C_LGREY, C_LGREY);
    v_put(WIN_R + 2,        WIN_C + WIN_W - 1, '^', C_DGREY, C_LGREY);
    v_put(WIN_R + WIN_H - 2,WIN_C + WIN_W - 1, 'v', C_DGREY, C_LGREY);

    /* Barre de statut */
    char st[48];
    /* Construire "Ln X, Col Y" */
    int si = 0;
    st[si++]='L'; st[si++]='n'; st[si++]=' ';
    int ln = cur_r + 1;
    if (ln >= 10) st[si++] = (char)('0' + ln / 10);
    st[si++] = (char)('0' + ln % 10);
    st[si++]=','; st[si++]=' ';
    st[si++]='C'; st[si++]='o'; st[si++]='l'; st[si++]=' ';
    int cn = cur_c + 1;
    if (cn >= 10) st[si++] = (char)('0' + cn / 10);
    st[si++] = (char)('0' + cn % 10);
    st[si++]=' '; st[si++]='|'; st[si++]=' ';
    st[si++]='U'; st[si++]='T'; st[si++]='F';
    st[si++]='-'; st[si++]='8';
    st[si] = '\0';

    v_statusbar(WIN_R + WIN_H - 1, WIN_C, WIN_W,
                st, dirty ? "* Modifie" : "Sauvegarde");
}

void np_key(char k) {
    if (k == KEY_NULL) return;
    dirty = 1;

    if (k == KEY_BACKSPACE) {
        if (cur_c > 0) {
            cur_c--;
            int c;
            for (c = cur_c; c < NP_COLS - 2; c++)
                buf[cur_r][c] = buf[cur_r][c + 1];
            buf[cur_r][NP_COLS - 2] = '\0';
        } else if (cur_r > 0) {
            cur_r--;
            cur_c = row_len(cur_r);
        }
    } else if (k == KEY_DELETE) {
        int c;
        for (c = cur_c; c < NP_COLS - 2; c++)
            buf[cur_r][c] = buf[cur_r][c + 1];
        buf[cur_r][NP_COLS - 2] = '\0';
    } else if (k == KEY_ENTER) {
        if (cur_r < NP_ROWS - 1) { cur_r++; cur_c = 0; }
    } else if (k == KEY_UP) {
        if (cur_r > 0) {
            cur_r--;
            int len = row_len(cur_r);
            if (cur_c > len) cur_c = len;
        }
    } else if (k == KEY_DOWN) {
        if (cur_r < NP_ROWS - 1) {
            cur_r++;
            int len = row_len(cur_r);
            if (cur_c > len) cur_c = len;
        }
    } else if (k == KEY_LEFT) {
        if (cur_c > 0) cur_c--;
        else if (cur_r > 0) { cur_r--; cur_c = row_len(cur_r); }
    } else if (k == KEY_RIGHT) {
        if (cur_c < row_len(cur_r)) cur_c++;
        else if (cur_r < NP_ROWS - 1) { cur_r++; cur_c = 0; }
    } else if (k == KEY_HOME) {
        cur_c = 0;
    } else if (k == KEY_END) {
        cur_c = row_len(cur_r);
    } else if (k == KEY_TAB) {
        int i;
        for (i = 0; i < 4 && cur_c < NP_COLS - 2; i++) {
            int c;
            for (c = NP_COLS - 2; c > cur_c; c--)
                buf[cur_r][c] = buf[cur_r][c - 1];
            buf[cur_r][cur_c++] = ' ';
        }
    } else if (k >= 0x20 && (unsigned char)k < 0x7F) {
        if (cur_c < NP_COLS - 2) {
            int c;
            for (c = NP_COLS - 2; c > cur_c; c--)
                buf[cur_r][c] = buf[cur_r][c - 1];
            buf[cur_r][cur_c++] = k;
        }
    }

    np_draw();
}