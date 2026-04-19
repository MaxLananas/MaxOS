#ifndef UI_H
#define UI_H

void ui_init(void);
void ui_topbar(int active);
void ui_taskbar(int active);
void ui_draw_window(unsigned int x, unsigned int y, unsigned int width, unsigned int height, const char* title);
void ui_draw_button(unsigned int x, unsigned int y, unsigned int width, unsigned int height, const char* text);
void ui_draw_menu(unsigned int x, unsigned int y, const char** items, unsigned int count);
void ui_draw_terminal(unsigned int x, unsigned int y, unsigned int width, unsigned int height);
void ui_draw_desktop(void);

#endif