#ifndef UI_H
#define UI_H

/* Dimensions bureau */
#define DESKTOP_R    1          /* Ligne début bureau */
#define DESKTOP_H   23          /* Hauteur bureau */
#define DESKTOP_C    0
#define DESKTOP_W   80

/* Fenêtre plein écran */
#define WIN_R        1
#define WIN_C        0
#define WIN_H       23
#define WIN_W       80

/* Zone de contenu (sans titlebar + menubar + statusbar) */
#define CONTENT_R   (WIN_R + 2)
#define CONTENT_C   (WIN_C + 1)
#define CONTENT_H   (WIN_H - 4)
#define CONTENT_W   (WIN_W - 2)

void ui_init(void);
void ui_topbar(int active);
void ui_taskbar(int active);
void ui_desktop(void);

#endif