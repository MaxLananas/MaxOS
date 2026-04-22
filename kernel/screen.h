#ifndef SCREEN_H
#define SCREEN_H

void screen_init(void);
void screen_clear(void);
void screen_putchar(char c, unsigned char color);
void screen_write(const char *str, unsigned char color);
void screen_writeln(const char *str, unsigned char color);
void screen_set_color(unsigned char color);
int screen_get_row(void);
void screen_scroll(void);

#endif