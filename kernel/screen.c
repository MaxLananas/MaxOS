#include "screen.h"
#include "io.h"

#define VGA_ADDRESS 0xB8000
#define VGA_WIDTH 80
#define VGA_HEIGHT 25

unsigned short *vga_buffer = (unsigned short *)VGA_ADDRESS;
unsigned char color = 0x0F;
unsigned int cursor_row = 0;
unsigned int cursor_col = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (unsigned int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga_buffer[i] = (color << 8) | ' ';
    }
    cursor_row = 0;
    cursor_col = 0;
}

void screen_putchar(char c, unsigned char col) {
    if (col != 0xFF) color = col;

    if (c == '\n') {
        cursor_col = 0;
        cursor_row++;
    } else {
        vga_buffer[cursor_row * VGA_WIDTH + cursor_col] = (color << 8) | c;
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

void screen_write(const char *str, unsigned char col) {
    while (*str) {
        screen_putchar(*str++, col);
    }
}

void screen_writeln(const char *str, unsigned char col) {
    screen_write(str, col);
    screen_putchar('\n', 0xFF);
}

void screen_set_color(unsigned char col) {
    color = col;
}

int screen_get_row(void) {
    return cursor_row;
}

void screen_scroll(void) {
    for (unsigned int i = 0; i < VGA_WIDTH * (VGA_HEIGHT - 1); i++) {
        vga_buffer[i] = vga_buffer[i + VGA_WIDTH];
    }

    for (unsigned int i = VGA_WIDTH * (VGA_HEIGHT - 1); i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga_buffer[i] = (color << 8) | ' ';
    }

    cursor_row = VGA_HEIGHT - 1;
    cursor_col = 0;
}