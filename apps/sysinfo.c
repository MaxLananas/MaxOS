#include "sysinfo.h"
#include "../drivers/screen.h"
#include "../ui/ui.h"

void si_draw(void) {
    v_window(WIN_R, WIN_C, WIN_H, WIN_W,
             "Parametres systeme - MaxOS", 1);

    const char* menu[] = { "Vue d'ensemble", "Performances", "Avance" };
    v_menubar(WIN_R+1, WIN_C, WIN_W, menu, 3);

    int r = WIN_R + 2;

    /* ─── Bloc CPU ─── */
    v_fill(r, WIN_C+1, 1, WIN_W-2, C_WHITE, C_BLUE);
    v_str(r, WIN_C+2, " Processeur", C_WHITE, C_BLUE);
    r++;
    v_str(r++, WIN_C+3, "Architecture  :  x86  Intel / AMD",   C_BLACK, C_WHITE);
    v_str(r++, WIN_C+3, "Mode          :  32-bit Protected",    C_BLACK, C_WHITE);
    v_str(r++, WIN_C+3, "GDT           :  Chargee et active",   C_BLACK, C_WHITE);
    v_str(r++, WIN_C+3, "IDT           :  Non configuree",      C_BLACK, C_WHITE);

    /* ─── Bloc RAM ─── */
    v_fill(r, WIN_C+1, 1, WIN_W-2, C_WHITE, C_BLUE);
    v_str(r, WIN_C+2, " Memoire", C_WHITE, C_BLUE);
    r++;
    v_str(r++, WIN_C+3, "Conventionnelle  :  640 KB (0x00000 - 0x9FFFF)", C_BLACK, C_WHITE);
    v_str(r++, WIN_C+3, "Etendue          :  ~255 MB",                     C_BLACK, C_WHITE);
    v_str(r++, WIN_C+3, "Kernel           :  0x8000",                      C_BLACK, C_WHITE);
    v_str(r++, WIN_C+3, "VGA Buffer       :  0xB8000  (80x25x2 = 4000 B)", C_BLACK, C_WHITE);
    v_str(r++, WIN_C+3, "Stack            :  0x90000",                     C_BLACK, C_WHITE);

    /* ─── Bloc Affichage ─── */
    v_fill(r, WIN_C+1, 1, WIN_W-2, C_WHITE, C_BLUE);
    v_str(r, WIN_C+2, " Affichage & Entrees", C_WHITE, C_BLUE);
    r++;
    v_str(r++, WIN_C+3, "Mode video   :  VGA Texte 80x25",         C_BLACK, C_WHITE);
    v_str(r++, WIN_C+3, "Couleurs     :  16 (palette 4-bit)",       C_BLACK, C_WHITE);
    v_str(r++, WIN_C+3, "Clavier      :  PS/2 AZERTY Scancode 1",  C_BLACK, C_WHITE);
    v_str(r++, WIN_C+3, "Souris       :  Non supportee",            C_BLACK, C_WHITE);

    /* ─── Statut ─── */
    v_fill(r, WIN_C+1, 1, WIN_W-2, C_WHITE, C_BLUE);
    v_str(r, WIN_C+2, " Statut", C_WHITE, C_BLUE);
    r++;
    v_str(r++, WIN_C+3, "Kernel    :  OK", C_LGREEN, C_WHITE);
    v_str(r++, WIN_C+3, "VGA       :  OK", C_LGREEN, C_WHITE);
    v_str(r,   WIN_C+3, "Clavier   :  OK", C_LGREEN, C_WHITE);

    v_statusbar(WIN_R+WIN_H-1, WIN_C, WIN_W,
                "Systeme operationnel", "F1-F4: changer d'app");
}