#include "screen.h"
#include "io.h"

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY 0xB8000

unsigned short *vga_buffer = (unsigned short*)VGA_MEMORY;
unsigned char color = 0x0F;
unsigned int cursor_row = 0;
unsigned int cursor_col = 0;

void screen_init() {
    screen_clear();
}

void screen_clear() {
    for (unsigned int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga_buffer[i] = (color << 8) | ' ';
    }
    cursor_row = 0;
    cursor_col = 0;
}

void screen_putchar(char c, unsigned char color) {
    if (c == '\n') {
        cursor_col = 0;
        cursor_row++;
    } else {
        unsigned int index = cursor_row * VGA_WIDTH + cursor_col;
        vga_buffer[index] = (color << 8) | c;
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

int screen_get_row() {
    return cursor_row;
}

void screen_scroll() {
    for (unsigned int i = 0; i < VGA_HEIGHT - 1; i++) {
        for (unsigned int j = 0; j < VGA_WIDTH; j++) {
            vga_buffer[i * VGA_WIDTH + j] = vga_buffer[(i + 1) * VGA_WIDTH + j];
        }
    }

    for (unsigned int j = 0; j < VGA_WIDTH; j++) {
        vga_buffer[(VGA_HEIGHT - 1) * VGA_WIDTH + j] = (color << 8) | ' ';
    }

    cursor_row--;
}