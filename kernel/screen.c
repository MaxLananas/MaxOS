#include "screen.h"
#include "io.h"

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY 0xB8000

static unsigned int cursor_row = 0;
static unsigned int cursor_col = 0;
static unsigned char color = 0x0F;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    unsigned short *vga = (unsigned short*)VGA_MEMORY;
    for (int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga[i] = (color << 8) | ' ';
    }
    cursor_row = 0;
    cursor_col = 0;
}

void screen_putchar(char c, unsigned char col) {
    unsigned short *vga = (unsigned short*)VGA_MEMORY;
    unsigned short val = (col << 8) | (unsigned char)c;

    if (c == '\n') {
        cursor_col = 0;
        cursor_row++;
    } else {
        vga[cursor_row * VGA_WIDTH + cursor_col] = val;
        cursor_col++;
        if (cursor_col >= VGA_WIDTH) {
            cursor_col = 0;
            cursor_row++;
        }
    }

    if (cursor_row >= VGA_HEIGHT) {
        screen_scroll();
    }
}

void screen_write(const char *str, unsigned char col) {
    while (*str) {
        screen_putchar(*str++, col);
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
    return cursor_row;
}

void screen_scroll(void) {
    unsigned short *vga = (unsigned short*)VGA_MEMORY;
    for (int i = 0; i < VGA_WIDTH * (VGA_HEIGHT - 1); i++) {
        vga[i] = vga[i + VGA_WIDTH];
    }
    for (int i = VGA_WIDTH * (VGA_HEIGHT - 1); i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga[i] = (color << 8) | ' ';
    }
    cursor_row--;
}