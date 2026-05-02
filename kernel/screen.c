#include "screen.h"
#include "io.h"

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY 0xB8000

static unsigned int cursor_row = 0;
static unsigned int cursor_col = 0;
static unsigned char color = 0x07;

void screen_init(void) {
    unsigned short *vga = (unsigned short*)VGA_MEMORY;
    for (unsigned int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga[i] = (color << 8) | ' ';
    }
    cursor_row = 0;
    cursor_col = 0;
}

void screen_clear(void) {
    unsigned short *vga = (unsigned short*)VGA_MEMORY;
    for (unsigned int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga[i] = (color << 8) | ' ';
    }
    cursor_row = 0;
    cursor_col = 0;
}

void screen_putchar(char c, unsigned char color) {
    unsigned short *vga = (unsigned short*)VGA_MEMORY;
    unsigned short attr = color << 8;
    unsigned short *pos = vga + (cursor_row * VGA_WIDTH + cursor_col);

    if (c == '\n') {
        cursor_col = 0;
        cursor_row++;
    } else {
        *pos = attr | (unsigned char)c;
        cursor_col++;
    }

    if (cursor_col >= VGA_WIDTH) {
        cursor_col = 0;
        cursor_row++;
    }

    if (cursor_row >= VGA_HEIGHT) {
        screen_scroll();
    }
}

void screen_write(const char *str, unsigned char color) {
    while (*str) {
        screen_putchar(*str++, color);
    }
}

void screen_writeln(const char *str, unsigned char color) {
    screen_write(str, color);
    screen_putchar('\n', color);
}

void screen_set_color(unsigned char new_color) {
    color = new_color;
}

int screen_get_row(void) {
    return cursor_row;
}

void screen_scroll(void) {
    unsigned short *vga = (unsigned short*)VGA_MEMORY;
    for (unsigned int i = 0; i < VGA_WIDTH * (VGA_HEIGHT - 1); i++) {
        vga[i] = vga[i + VGA_WIDTH];
    }
    for (unsigned int i = VGA_WIDTH * (VGA_HEIGHT - 1); i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga[i] = (color << 8) | ' ';
    }
    cursor_row = VGA_HEIGHT - 1;
}