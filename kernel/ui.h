#ifndef UI_H
#define UI_H

void ui_draw_button(unsigned int x, unsigned int y, unsigned int width, unsigned int height, unsigned char fg, unsigned char bg, const char *text);
void ui_draw_window(unsigned int x, unsigned int y, unsigned int width, unsigned int height, const char *title);

#endif