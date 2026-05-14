#include "screen.h"
#include "io.h"

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY 0xB8000

unsigned char color = 0x0F;
unsigned short *vga_buffer = (unsigned short*)VGA_MEMORY;
unsigned int row = 0;
unsigned int col = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga_buffer[i] = (unsigned char)' ' | (color << 8);
    }
    row = 0;
    col = 0;
}

void screen_putchar(char c, unsigned char color) {
    if (c == '\n') {
        row++;
        col = 0;
    } else {
        vga_buffer[row * VGA_WIDTH + col] = (unsigned char)c | (color << 8);
        col++;
        if (col >= VGA_WIDTH) {
            row++;
            col = 0;
        }
    }
    if (row >= VGA_HEIGHT) {
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
    return row;
}

void screen_scroll(void) {
    for (int i = 0; i < VGA_WIDTH * (VGA_HEIGHT - 1); i++) {
        vga_buffer[i] = vga_buffer[i + VGA_WIDTH];
    }
    for (int i = VGA_WIDTH * (VGA_HEIGHT - 1); i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga_buffer[i] = (unsigned char)' ' | (color << 8);
    }
    row = VGA_HEIGHT - 1;
}