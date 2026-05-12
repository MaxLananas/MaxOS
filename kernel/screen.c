#include "screen.h"
#include "io.h"

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_ADDRESS 0xB8000

static unsigned int cursor_row = 0;
static unsigned int cursor_col = 0;
static unsigned char color = 0x0F;

void screen_init(void) {
    for (unsigned int i = 0; i < VGA_HEIGHT; i++) {
        for (unsigned int j = 0; j < VGA_WIDTH; j++) {
            unsigned short *vga = (unsigned short*)VGA_ADDRESS;
            vga[i * VGA_WIDTH + j] = (color << 8) | ' ';
        }
    }
}

void screen_clear(void) {
    screen_init();
    cursor_row = 0;
    cursor_col = 0;
}

void screen_putchar(char c, unsigned char color) {
    unsigned short *vga = (unsigned short*)VGA_ADDRESS;
    if (c == '\n') {
        cursor_col = 0;
        cursor_row++;
    } else {
        vga[cursor_row * VGA_WIDTH + cursor_col] = (color << 8) | c;
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
    unsigned short *vga = (unsigned short*)VGA_ADDRESS;
    for (unsigned int i = 1; i < VGA_HEIGHT; i++) {
        for (unsigned int j = 0; j < VGA_WIDTH; j++) {
            vga[(i - 1) * VGA_WIDTH + j] = vga[i * VGA_WIDTH + j];
        }
    }
    for (unsigned int j = 0; j < VGA_WIDTH; j++) {
        vga[(VGA_HEIGHT - 1) * VGA_WIDTH + j] = (color << 8) | ' ';
    }
    cursor_row--;
}