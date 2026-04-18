#include "about.h"
#include "../drivers/screen.h"
#include "../ui/ui.h"

void ab_draw(void) {
    v_window(WIN_R, WIN_C, WIN_H, WIN_W, "A propos de MaxOS", 1);

    const char* menu[] = { "Informations" };
    v_menubar(WIN_R+1, WIN_C, WIN_W, menu, 1);

    int r = WIN_R + 3;
    int c = 24;

    /* Logo ASCII art centré */
    v_str(r++, c, " __  __               ___  ____  ",  C_BLUE, C_WHITE);
    v_str(r++, c, "|  \\/  | __ _ __  __ / _ \\/ ___|",  C_BLUE, C_WHITE);
    v_str(r++, c, "| |\\/| |/ _` |\\ \\/ /| | | \\___ \\", C_BLUE, C_WHITE);
    v_str(r++, c, "| |  | | (_| | >  < | |_| |___) |", C_BLUE, C_WHITE);
    v_str(r++, c, "|_|  |_|\\__,_|/_/\\_\\ \\___/|____/ ", C_BLUE, C_WHITE);
    r++;
    v_str(r++, 30, "Systeme d'exploitation minimaliste",
          C_DGREY, C_WHITE);

    v_hl(r++, 10, 60, '-', C_LGREY, C_WHITE);

    /* Infos */
    const char* keys[] = {
        "Version      ", "Architecture ", "Langage      ",
        "Compilateur  ", "Emulateur    ", "Bootloader   ",
        "VGA          ", "Clavier      "
    };
    const char* vals[] = {
        "1.0.0",
        "x86 32-bit (Intel / AMD)",
        "C + Assembly x86 (NASM)",
        "GCC cross-compile -m32",
        "QEMU qemu-system-i386",
        "Custom MBR 512 bytes",
        "Texte 80x25 - 16 couleurs",
        "PS/2 AZERTY Scancode Set 1"
    };
    int i;
    for (i = 0; i < 8; i++) {
        v_str(r,   14, keys[i], C_DGREY, C_WHITE);
        v_put(r,   27, ':', C_LGREY, C_WHITE);
        v_str(r++, 29, vals[i], C_BLACK, C_WHITE);
    }

    v_hl(r++, 10, 60, '-', C_LGREY, C_WHITE);
    v_str(r++, 18, "Fait avec passion en C et ASM x86 !",
          C_DGREY, C_WHITE);

    /* Bouton OK centré */
    v_fill(r, 35, 1, 12, C_WHITE, C_BLUE);
    v_str(r, 37, "   OK   ", C_WHITE, C_BLUE);

    v_statusbar(WIN_R+WIN_H-1, WIN_C, WIN_W,
                "MaxOS v1.0 - 2024", "OK");
}