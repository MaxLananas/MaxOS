#include "screen.h"
#include "io.h"

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY 0xB8000

unsigned char color = 0x0F;
unsigned short *vga_buffer = (unsigned short*)VGA_MEMORY;
unsigned int vga_row = 0;
unsigned int vga_col = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (unsigned int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga_buffer[i] = (color << 8) | ' ';
    }
    vga_row = 0;
    vga_col = 0;
}

void screen_putchar(char c, unsigned char color) {
    if (c == '\n') {
        vga_row++;
        vga_col = 0;
    } else {
        vga_buffer[vga_row * VGA_WIDTH + vga_col] = (color << 8) | c;
        vga_col++;
        if (vga_col >= VGA_WIDTH) {
            vga_row++;
            vga_col = 0;
        }
    }
    if (vga_row >= VGA_HEIGHT) {
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
    return vga_row;
}

void screen_scroll(void) {
    for (unsigned int i = 0; i < VGA_HEIGHT - 1; i++) {
        for (unsigned int j = 0; j < VGA_WIDTH; j++) {
            vga_buffer[i * VGA_WIDTH + j] = vga_buffer[(i + 1) * VGA_WIDTH + j];
        }
    }
    for (unsigned int j = 0; j < VGA_WIDTH; j++) {
        vga_buffer[(VGA_HEIGHT - 1) * VGA_WIDTH + j] = (color << 8) | ' ';
    }
    vga_row = VGA_HEIGHT - 1;
    vga_col = 0;
}