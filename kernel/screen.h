#ifndef SCREEN_H
#define SCREEN_H

#define COLOR_BLACK        0x00
#define COLOR_BLUE         0x01
#define COLOR_GREEN        0x02
#define COLOR_CYAN         0x03
#define COLOR_RED          0x04
#define COLOR_MAGENTA      0x05
#define COLOR_BROWN        0x06
#define COLOR_LIGHT_GREY   0x07
#define COLOR_DARK_GREY    0x08
#define COLOR_LIGHT_BLUE   0x09
#define COLOR_LIGHT_GREEN  0x0A
#define COLOR_LIGHT_CYAN   0x0B
#define COLOR_LIGHT_RED    0x0C
#define COLOR_PINK         0x0D
#define COLOR_YELLOW       0x0E
#define COLOR_WHITE        0x0F

#define MAKE_COLOR(fg, bg) ((bg << 4) | fg)

void screen_init(void);
void screen_clear(void);
void screen_putchar(char c, unsigned char color);
void screen_write(const char *str, unsigned char color);
void screen_writeln(const char *str, unsigned char color);
void screen_set_color(unsigned char color);
int  screen_get_row(void);
void screen_scroll(void);
void screen_set_cursor(int row, int col);

#endif
