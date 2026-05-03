#include "screen.h"
#include "io.h"

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY 0xB8000

static unsigned char color = 0x0F;
static unsigned short *vga_buffer = (unsigned short*)VGA_MEMORY;
static unsigned int row = 0;
static unsigned int col = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (unsigned int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga_buffer[i] = (unsigned short)0x20 | (color << 8);
    }
    row = 0;
    col = 0;
}

void screen_putchar(char c, unsigned char c_color) {
    if (c == '\n') {
        col = 0;
        row++;
    } else {
        vga_buffer[row * VGA_WIDTH + col] = (unsigned short)c | (c_color << 8);
        col++;
    }

    if (col >= VGA_WIDTH) {
        col = 0;
        row++;
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
    for (unsigned int i = 0; i < VGA_WIDTH * (VGA_HEIGHT - 1); i++) {
        vga_buffer[i] = vga_buffer[i + VGA_WIDTH];
    }

    for (unsigned int i = VGA_WIDTH * (VGA_HEIGHT - 1); i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga_buffer[i] = (unsigned short)0x20 | (color << 8);
    }

    row = VGA_HEIGHT - 1;
    col = 0;
}