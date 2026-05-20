#include "screen.h"
#include "io.h"

static unsigned int cursor_x = 0;
static unsigned int cursor_y = 0;
static unsigned char color = 0x0F;

void screen_init(void) {
    cursor_x = 0;
    cursor_y = 0;
    color = 0x0F;
    screen_clear();
}

void screen_clear(void) {
    unsigned char *video = (unsigned char *)0xB8000;
    for (int i = 0; i < 80 * 25 * 2; i += 2) {
        video[i] = ' ';
        video[i + 1] = color;
    }
    cursor_x = 0;
    cursor_y = 0;
    screen_move_cursor();
}

void screen_putchar(char c, unsigned char col) {
    unsigned char *video = (unsigned char *)0xB8000;
    if (c == '\n') {
        cursor_x = 0;
        cursor_y++;
    } else {
        video[(cursor_y * 80 + cursor_x) * 2] = c;
        video[(cursor_y * 80 + cursor_x) * 2 + 1] = col;
        cursor_x++;
    }
    if (cursor_x >= 80) {
        cursor_x = 0;
        cursor_y++;
    }
    if (cursor_y >= 25) {
        screen_scroll();
    }
    screen_move_cursor();
}

void screen_write(const char *str, unsigned char col) {
    for (int i = 0; str[i]; i++) {
        screen_putchar(str[i], col);
    }
}

void screen_writeln(const char *str, unsigned char col) {
    screen_write(str, col);
    screen_putchar('\n', col);
}

void screen_set_color(unsigned char col) {
    color = col;
}

int screen_get_row(void) {
    return cursor_y;
}

void screen_scroll(void) {
    unsigned char *video = (unsigned char *)0xB8000;
    for (int y = 1; y < 25; y++) {
        for (int x = 0; x < 80; x++) {
            video[((y - 1) * 80 + x) * 2] = video[(y * 80 + x) * 2];
            video[((y - 1) * 80 + x) * 2 + 1] = video[(y * 80 + x) * 2 + 1];
        }
    }
    for (int x = 0; x < 80; x++) {
        video[(24 * 80 + x) * 2] = ' ';
        video[(24 * 80 + x) * 2 + 1] = color;
    }
    cursor_y = 24;
}

static void screen_move_cursor(void) {
    unsigned short pos = cursor_y * 80 + cursor_x;
    outb(0x3D4, 0x0F);
    outb(0x3D5, (unsigned char)(pos & 0xFF));
    outb(0x3D4, 0x0E);
    outb(0x3D5, (unsigned char)((pos >> 8) & 0xFF));
}