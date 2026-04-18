#include "ui.h"
#include "../drivers/screen.h"

/* ══════════════════════════════════════════
   TOPBAR  (barre du haut fixe)
══════════════════════════════════════════ */
void ui_topbar(int active) {
    /* Fond blanc pur */
    v_fill(0, 0, 1, VGA_W, C_BLACK, C_WHITE);

    /* Séparateur bas très fin */
    v_hl(0, 0, VGA_W, ' ', C_DGREY, C_WHITE);

    /* Logo gauche */
    v_put(0, 1, 'M', C_BLUE,  C_WHITE);
    v_put(0, 2, 'a', C_BLUE,  C_WHITE);
    v_put(0, 3, 'x', C_BLUE,  C_WHITE);
    v_put(0, 4, 'O', C_DGREY, C_WHITE);
    v_put(0, 5, 'S', C_DGREY, C_WHITE);

    /* Séparateur vertical */
    v_put(0, 7, '|', C_LGREY, C_WHITE);

    /* Onglets centrés */
    const char* tabs[4] = {
        "  Notes  ",
        "  Terminal  ",
        "  Systeme  ",
        "  A propos  "
    };
    int positions[4] = { 9, 19, 32, 44 };
    int i;
    for (i = 0; i < 4; i++) {
        if (i == active) {
            /* Onglet actif : fond bleu, texte blanc */
            v_str(0, positions[i], tabs[i], C_WHITE, C_BLUE);
            /* Indicateur bas */
            int l = 0;
            while (tabs[i][l]) l++;
        } else {
            v_str(0, positions[i], tabs[i], C_DGREY, C_WHITE);
        }
    }

    v_put(0, 57, '|', C_LGREY, C_WHITE);
}

/* ══════════════════════════════════════════
   TASKBAR  (barre du bas - style Win11)
══════════════════════════════════════════ */
void ui_taskbar(int active) {
    int r = VGA_H - 1;

    /* Fond blanc */
    v_fill(r, 0, 1, VGA_W, C_BLACK, C_WHITE);

    /* Séparateur haut */
    v_hl(r, 0, VGA_W, ' ', C_DGREY, C_WHITE);

    /* Bouton Start style Win11 */
    v_str(r, 1, "[", C_LGREY, C_WHITE);
    v_str(r, 2, "MaxOS", C_BLUE, C_WHITE);
    v_str(r, 7, "]", C_LGREY, C_WHITE);

    v_put(r, 9, '|', C_LGREY, C_WHITE);

    /* Apps */
    const char* apps[4] = {
        " Notes ", " Term ", " Sys ", " Info "
    };
    int acols[4] = { 11, 19, 26, 32 };
    int colors[4] = { C_BLUE, C_GREEN, C_MAGENTA, C_CYAN };
    int i;
    for (i = 0; i < 4; i++) {
        int bg = (i == active) ? C_LGREY : C_WHITE;
        v_str(r, acols[i], apps[i], colors[i], bg);
    }

    v_put(r, 39, '|', C_LGREY, C_WHITE);

    /* Info droite */
    v_str(r, 41, "F1 Notes  F2 Term  F3 Sys  F4 About",
          C_DGREY, C_WHITE);
}

/* ══════════════════════════════════════════
   DESKTOP  (bureau vide si aucune app)
══════════════════════════════════════════ */
void ui_desktop(void) {
    v_fill(DESKTOP_R, DESKTOP_C, DESKTOP_H, DESKTOP_W,
           C_DGREY, C_LGREY);
}

void ui_init(void) {
    v_init();
}