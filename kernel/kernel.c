#include "../drivers/screen.h"
#include "../drivers/keyboard.h"
#include "../ui/ui.h"
#include "../apps/notepad.h"
#include "../apps/terminal.h"
#include "../apps/sysinfo.h"
#include "../apps/about.h"
#include "idt.h" /* Ajout de l'include pour l'IDT */

unsigned int CLK_H = 14;
unsigned int CLK_M = 30;
unsigned int CLK_S = 0;

static int active = 0;

static void itoa2(unsigned int n, char* b) {
    b[0] = (char)('0' + (n / 10) % 10);
    b[1] = (char)('0' + n % 10);
    b[2] = '\0';
}

static void clock_tick(void) {
    CLK_S++;
    if (CLK_S >= 60) { CLK_S = 0; CLK_M++; }
    if (CLK_M >= 60) { CLK_M = 0; CLK_H++; }
    if (CLK_H >= 24)   CLK_H = 0;
}

static void clock_draw(void) {
    char h[3], m[3], s[3];
    itoa2(CLK_H, h);
    itoa2(CLK_M, m);
    itoa2(CLK_S, s);
    v_fill(0, 58, 1, 22, C_BLACK, C_WHITE);
    v_str(0, 58, h, C_BLACK, C_WHITE);
    v_put(0, 60, ':', C_DGREY, C_WHITE);
    v_str(0, 61, m, C_BLACK, C_WHITE);
    v_put(0, 63, ':', C_DGREY, C_WHITE);
    v_str(0, 64, s, C_DGREY, C_WHITE);
    v_str(0, 67, "  (wifi) [###]", C_DGREY, C_WHITE);
}

static void redraw_app(void) {
    switch (active) {
        case 0: np_draw(); break;
        case 1: tm_draw(); break;
        case 2: si_draw(); break;
        case 3: ab_draw(); break;
    }
    ui_topbar(active);
    ui_taskbar(active);
}

static void delay(unsigned int n) {
    volatile unsigned int i;
    for (i = 0; i < n; i++) __asm__ volatile("nop");
}

/* Définitions factices pour résoudre les erreurs de linkage */
void si_key(char k) {
    /* Ne fait rien, car le code source de sysinfo n'est pas fourni */
    (void)k; /* Supprime l'avertissement de variable non utilisée */
}

void ab_key(char k) {
    /* Ne fait rien, car le code source d'about n'est pas fourni */
    (void)k; /* Supprime l'avertissement de variable non utilisée */
}

void kernel_main(void) {
    v_init();
    kb_init();
    idt_init(); /* Initialisation de l'IDT et du PIC */

    np_init();
    tm_init();

    ui_topbar(active);
    ui_taskbar(active);
    np_draw();

    unsigned int t = 0;

    while (1) {
        delay(1); /* Un petit délai pour éviter une boucle trop serrée */
        t++;

        if (t % 4000000 == 0) { /* Fréquence de rafraîchissement de l'horloge */
            clock_tick();
            clock_draw();
        }

        if (!kb_haskey()) continue;

        char k = kb_getchar();
        if (k == KEY_NULL) continue;

        /* ══════════════════════════════════
           NAVIGATION ENTRE APPS
           F1/F2/F3/F4 ET aussi 1/2/3/4
           au cas où QEMU intercepte les F
        ══════════════════════════════════ */

        /* Méthode 1 : touches F */
        if (k == KEY_F1) { active = 0; redraw_app(); continue; }
        if (k == KEY_F2) { active = 1; redraw_app(); continue; }
        if (k == KEY_F3) { active = 2; redraw_app(); continue; }
        if (k == KEY_F4) { active = 3; redraw_app(); continue; }

        /* Méthode 2 : TAB = naviguer entre apps */
        if (k == KEY_TAB) {
            active = (active + 1) % 4;
            redraw_app();
            continue;
        }

        /* Dispatcher */
        switch (active) {
            case 0: np_key(k); break;
            case 1: tm_key(k); break;
            case 2: si_key(k); break; /* Appel à la fonction factice */
            case 3: ab_key(k); break; /* Appel à la fonction factice */
            default: break;
        }

        ui_topbar(active);
        ui_taskbar(active);
    }
}