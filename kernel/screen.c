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
    for (unsigned int i = 0; i < VGA_HEIGHT; i++) {
        for (unsigned int j = 0; j < VGA_WIDTH; j++) {
            vga_buffer[i * VGA_WIDTH + j] = (color << 8) | ' ';
        }
    }
    row = 0;
    col = 0;
}

void screen_clear(void) {
    for (unsigned int i = 0; i < VGA_HEIGHT; i++) {
        for (unsigned int j = 0; j < VGA_WIDTH; j++) {
            vga_buffer[i * VGA_WIDTH + j] = (color << 8) | ' ';
        }
    }
    row = 0;
    col = 0;
}

void screen_putchar(char c, unsigned char clr) {
    if (clr != 0) color = clr;

    if (c == '\n') {
        col = 0;
        row++;
    } else {
        vga_buffer[row * VGA_WIDTH + col] = (color << 8) | c;
        col++;
        if (col >= VGA_WIDTH) {
            col = 0;
            row++;
        }
    }

    if (row >= VGA_HEIGHT) {
        screen_scroll();
        row = VGA_HEIGHT - 1;
    }
}

void screen_write(const char *str, unsigned char clr) {
    while (*str) {
        screen_putchar(*str++, clr);
    }
}

void screen_writeln(const char *str, unsigned char clr) {
    screen_write(str, clr);
    screen_putchar('\n', clr);
}

void screen_set_color(unsigned char clr) {
    color = clr;
}

int screen_get_row(void) {
    return row;
}

void screen_scroll(void) {
    for (unsigned int i = 1; i < VGA_HEIGHT; i++) {
        for (unsigned int j = 0; j < VGA_WIDTH; j++) {
            vga_buffer[(i - 1) * VGA_WIDTH + j] = vga_buffer[i * VGA_WIDTH + j];
        }
    }
    for (unsigned int j = 0; j < VGA_WIDTH; j++) {
        vga_buffer[(VGA_HEIGHT - 1) * VGA_WIDTH + j] = (color << 8) | ' ';
    }
}