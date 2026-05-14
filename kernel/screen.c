#include "screen.h"
#include "io.h"

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY 0xB8000

unsigned char color = 0x0F;
unsigned short *vga_buffer = (unsigned short*)VGA_MEMORY;
unsigned int vga_index = 0;
unsigned int row = 0;
unsigned int column = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (unsigned int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga_buffer[i] = (unsigned short)0x20 | (color << 8);
    }
    vga_index = 0;
    row = 0;
    column = 0;
}

void screen_putchar(char c, unsigned char color) {
    if (c == '\n') {
        row++;
        column = 0;
    } else {
        vga_buffer[vga_index] = (unsigned short)c | (color << 8);
        vga_index++;
        column++;
        if (column >= VGA_WIDTH) {
            row++;
            column = 0;
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
    for (unsigned int i = 0; i < VGA_HEIGHT - 1; i++) {
        for (unsigned int j = 0; j < VGA_WIDTH; j++) {
            vga_buffer[i * VGA_WIDTH + j] = vga_buffer[(i + 1) * VGA_WIDTH + j];
        }
    }
    for (unsigned int j = 0; j < VGA_WIDTH; j++) {
        vga_buffer[(VGA_HEIGHT - 1) * VGA_WIDTH + j] = (unsigned short)0x20 | (color << 8);
    }
    row = VGA_HEIGHT - 1;
    column = 0;
}