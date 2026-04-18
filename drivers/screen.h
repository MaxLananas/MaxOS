#ifndef SCREEN_H
#define SCREEN_H

/* Palette 16 couleurs VGA */
#define C_BLACK      0
#define C_BLUE       1
#define C_GREEN      2
#define C_CYAN       3
#define C_RED        4
#define C_MAGENTA    5
#define C_BROWN      6
#define C_LGREY      7   /* Light Grey  = blanc cassé */
#define C_DGREY      8   /* Dark Grey   = gris foncé  */
#define C_LBLUE      9
#define C_LGREEN    10
#define C_LCYAN     11
#define C_LRED      12
#define C_LMAGENTA  13
#define C_YELLOW    14
#define C_WHITE     15

#define VGA_W   80
#define VGA_H   25
#define VGA_MEM 0xB8000

/* Primitives */
void v_init(void);
void v_put(int r, int c, char ch, int fg, int bg);
void v_str(int r, int c, const char* s, int fg, int bg);
void v_fill(int r, int c, int h, int w, int fg, int bg);
void v_hl(int r, int c, int len, char ch, int fg, int bg);
void v_vl(int r, int c, int len, char ch, int fg, int bg);

/* Composants */
void v_titlebar(int r, int c, int w,
                const char* title, int focused);
void v_menubar(int r, int c, int w,
               const char** items, int n);
void v_statusbar(int r, int c, int w,
                 const char* left, const char* right);
void v_window(int r, int c, int h, int w,
              const char* title, int focused);
void v_button(int r, int c, const char* label,
              int fg, int bg);
void v_int(int r, int c, int n, int fg, int bg);
void v_int2(int r, int c, unsigned int n, int fg, int bg);

#endif