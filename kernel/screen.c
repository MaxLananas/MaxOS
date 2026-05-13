#include "screen.h"
#include "io.h"

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_ADDRESS 0xB8000

unsigned short *vga_buffer = (unsigned short*)VGA_ADDRESS;
unsigned char terminal_color = 0x0F;
unsigned int terminal_row = 0;
unsigned int terminal_column = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (unsigned int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga_buffer[i] = (unsigned short)0x20 | (terminal_color << 8);
    }
    terminal_row = 0;
    terminal_column = 0;
}

void screen_putchar(char c, unsigned char color) {
    if (c == '\n') {
        terminal_column = 0;
        terminal_row++;
    } else {
        vga_buffer[terminal_row * VGA_WIDTH + terminal_column] = (unsigned short)c | (color << 8);
        terminal_column++;
    }

    if (terminal_column >= VGA_WIDTH) {
        terminal_column = 0;
        terminal_row++;
    }

    if (terminal_row >= VGA_HEIGHT) {
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

void screen_set_color(unsigned char color) {
    terminal_color = color;
}

int screen_get_row(void) {
    return terminal_row;
}

void screen_scroll(void) {
    for (unsigned int i = 0; i < VGA_WIDTH * (VGA_HEIGHT - 1); i++) {
        vga_buffer[i] = vga_buffer[i + VGA_WIDTH];
    }

    for (unsigned int i = VGA_WIDTH * (VGA_HEIGHT - 1); i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga_buffer[i] = (unsigned short)0x20 | (terminal_color << 8);
    }

    terminal_row = VGA_HEIGHT - 1;
}