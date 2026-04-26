#include "screen.h"
#include "io.h"

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY 0xB8000

unsigned short *vga_buffer = (unsigned short*)VGA_MEMORY;
unsigned char color = 0x0F;
unsigned int row = 0;
unsigned int col = 0;

void screen_init(void) {
    for (int i = 0; i < VGA_HEIGHT; i++) {
        for (int j = 0; j < VGA_WIDTH; j++) {
            vga_buffer[i * VGA_WIDTH + j] = (color << 8) | ' ';
        }
    }
    row = 0;
    col = 0;
}

void screen_clear(void) {
    screen_init();
}

void screen_putchar(char c, unsigned char c_color) {
    if (c == '\n') {
        row++;
        col = 0;
    } else {
        vga_buffer[row * VGA_WIDTH + col] = (c_color << 8) | c;
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

void screen_write(const char *str, unsigned char c_color) {
    while (*str) {
        screen_putchar(*str++, c_color);
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
    for (int i = 1; i < VGA_HEIGHT; i++) {
        for (int j = 0; j < VGA_WIDTH; j++) {
            vga_buffer[(i-1) * VGA_WIDTH + j] = vga_buffer[i * VGA_WIDTH + j];
        }
    }
    for (int j = 0; j < VGA_WIDTH; j++) {
        vga_buffer[(VGA_HEIGHT-1) * VGA_WIDTH + j] = (color << 8) | ' ';
    }
    row = VGA_HEIGHT - 1;
}