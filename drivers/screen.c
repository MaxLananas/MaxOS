#include "screen.h"

static unsigned char mkc(int fg, int bg) {
    return (unsigned char)((bg << 4) | (fg & 0xF));
}

void v_init(void) {
    unsigned short* m = (unsigned short*)VGA_MEM;
    unsigned char   k = mkc(C_WHITE, C_LGREY);
    int i;
    for (i = 0; i < VGA_W * VGA_H; i++)
        m[i] = ' ' | ((unsigned short)k << 8);
}

void v_put(int r, int c, char ch, int fg, int bg) {
    if (r < 0 || r >= VGA_H || c < 0 || c >= VGA_W) return;
    unsigned short* m = (unsigned short*)VGA_MEM;
    m[r * VGA_W + c] = (unsigned char)ch | ((unsigned short)mkc(fg,bg) << 8);
}

void v_str(int r, int c, const char* s, int fg, int bg) {
    int i = 0;
    while (s[i] && c + i < VGA_W) {
        v_put(r, c + i, s[i], fg, bg);
        i++;
    }
}

void v_fill(int r, int c, int h, int w, int fg, int bg) {
    int rr, cc;
    for (rr = r; rr < r + h && rr < VGA_H; rr++)
        for (cc = c; cc < c + w && cc < VGA_W; cc++)
            v_put(rr, cc, ' ', fg, bg);
}

void v_hl(int r, int c, int len, char ch, int fg, int bg) {
    int i;
    for (i = 0; i < len && c + i < VGA_W; i++)
        v_put(r, c + i, ch, fg, bg);
}

void v_vl(int r, int c, int len, char ch, int fg, int bg) {
    int i;
    for (i = 0; i < len && r + i < VGA_H; i++)
        v_put(r + i, c, ch, fg, bg);
}

/* Titlebar avec boutons style Win11 */
void v_titlebar(int r, int c, int w,
                const char* title, int focused) {
    int tbg = focused ? C_BLUE  : C_DGREY;
    int tfg = focused ? C_WHITE : C_LGREY;

    v_fill(r, c, 1, w, tfg, tbg);

    /* Titre centré */
    int tl  = 0; while (title[tl]) tl++;
    int pos = c + (w - tl) / 2;
    if (pos < c) pos = c;
    v_str(r, pos, title, tfg, tbg);

    /* Boutons droite : _ □ X */
    v_str(r, c + w - 12, " ", tfg, tbg);
    v_str(r, c + w - 11, " _ ", C_WHITE, C_DGREY);
    v_str(r, c + w - 8,  " + ", C_WHITE, C_DGREY);
    v_str(r, c + w - 5,  " X ", C_WHITE, C_LRED);
    v_str(r, c + w - 2,  "  ", tfg, tbg);
}

/* Barre de menu */
void v_menubar(int r, int c, int w,
               const char** items, int n) {
    v_fill(r, c, 1, w, C_DGREY, C_LGREY);
    int x = c + 1;
    int i;
    for (i = 0; i < n && x < c + w - 1; i++) {
        v_str(r, x, items[i], C_DGREY, C_LGREY);
        int l = 0; while (items[i][l]) l++;
        x += l + 2;
    }
}

/* Barre de statut */
void v_statusbar(int r, int c, int w,
                 const char* left, const char* right) {
    v_fill(r, c, 1, w, C_DGREY, C_LGREY);
    v_str(r, c + 2, left, C_DGREY, C_LGREY);
    if (right) {
        int rl = 0; while (right[rl]) rl++;
        v_str(r, c + w - rl - 2, right, C_DGREY, C_LGREY);
    }
}

/* Fenêtre complète */
void v_window(int r, int c, int h, int w,
              const char* title, int focused) {
    /* Ombre */
    v_fill(r + 1, c + 2, h, w, C_DGREY, C_DGREY);
    /* Corps */
    v_fill(r, c, h, w, C_BLACK, C_WHITE);
    /* Titlebar */
    v_titlebar(r, c, w, title, focused);
}

void v_button(int r, int c, const char* label,
              int fg, int bg) {
    v_put(r, c, ' ', fg, bg);
    int i = 0;
    while (label[i]) {
        v_put(r, c + 1 + i, label[i], fg, bg);
        i++;
    }
    v_put(r, c + 1 + i, ' ', fg, bg);
}

void v_int(int r, int c, int n, int fg, int bg) {
    char buf[12]; int i = 0;
    if (n == 0) { v_put(r, c, '0', fg, bg); return; }
    if (n < 0)  { v_put(r, c, '-', fg, bg); c++; n = -n; }
    char tmp[12]; int t = 0;
    while (n > 0) { tmp[t++] = (char)('0' + n % 10); n /= 10; }
    int j;
    for (j = t - 1; j >= 0; j--) buf[i++] = tmp[j];
    buf[i] = '\0';
    v_str(r, c, buf, fg, bg);
}

void v_int2(int r, int c, unsigned int n, int fg, int bg) {
    v_put(r, c,     (char)('0' + (n / 10) % 10), fg, bg);
    v_put(r, c + 1, (char)('0' + n % 10),         fg, bg);
}