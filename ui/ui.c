#include "screen.h"
#include "window.h"

void ui_draw_window(unsigned short x, unsigned short y, unsigned short width, unsigned short height, const unsigned char *title) {
    screen_set_color(0x0F, 0x01);
    screen_set_cursor(x, y);
    screen_putchar('+');
    for (unsigned short i = 1; i < width - 1; i++) screen_putchar('-');
    screen_putchar('+');

    screen_set_cursor(x, y + 1);
    screen_putchar('|');
    for (unsigned short i = 1; i < width - 1; i++) screen_putchar(' ');
    screen_putchar('|');

    screen_set_cursor(x + (width / 2) - (sizeof(title) / 2), y + 1);
    screen_write(title, sizeof(title) - 1);

    for (unsigned short i = 2; i < height - 1; i++) {
        screen_set_cursor(x, y + i);
        screen_putchar('|');
        for (unsigned short j = 1; j < width - 1; j++) screen_putchar(' ');
        screen_putchar('|');
    }

    screen_set_cursor(x, y + height - 1);
    screen_putchar('+');
    for (unsigned short i = 1; i < width - 1; i++) screen_putchar('-');
    screen_putchar('+');
}