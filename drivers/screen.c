#include "screen.h"
#include "../kernel/io.h"

static unsigned char color = 0x0F;
static unsigned int row = 0;
static unsigned int col = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    unsigned short *vidmem = (unsigned short*)0xB8000;
    for (unsigned int i = 0; i < 80 * 25; i++) {
        vidmem[i] = 0x0720;
    }
    row = 0;
    col = 0;
}

void screen_putchar(char c, unsigned char c_color) {
    unsigned short *vidmem = (unsigned short*)0xB8000;

    if (c == '\n') {
        row++;
        col = 0;
        if (row >= 25) {
            screen_scroll();
        }
        return;
    }

    vidmem[(row * 80) + col] = (c_color << 8) | c;
    col++;

    if (col >= 80) {
        row++;
        col = 0;
        if (row >= 25) {
            screen_scroll();
        }
    }
}

void screen_write(const char *str, unsigned char c_color) {
    while (*str) {
        screen_putchar(*str, c_color);
        str++;
    }
}

void screen_writeln(const char *str, unsigned char c_color) {
    screen_write(str, c_color);
    screen_putchar('\n', c_color);
}

void screen_set_color(unsigned char c_color) {
    color = c_color;
}

int screen_get_row(void) {
    return row;
}

void screen_scroll(void) {
    unsigned short *vidmem = (unsigned short*)0xB8000;

    for (unsigned int i = 0; i < 24 * 80; i++) {
        vidmem[i] = vidmem[i + 80];
    }

    for (unsigned int i = 24 * 80; i < 25 * 80; i++) {
        vidmem[i] = 0x0720;
    }

    row = 24;
}