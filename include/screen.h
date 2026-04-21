#ifndef SCREEN_H
#define SCREEN_H

void screen_clear();
void screen_putchar(unsigned char c);
void screen_write(const unsigned char *str, unsigned int len);
void screen_set_color(unsigned char fg, unsigned char bg);
void screen_get_cursor(unsigned short *x, unsigned short *y);
void screen_set_cursor(unsigned short x, unsigned short y);

#endif