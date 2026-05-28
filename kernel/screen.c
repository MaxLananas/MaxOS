#include "screen.h"
#include "io.h"

#define VGA_ADDRESS 0xB8000
#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_COLOR_DEFAULT 0x0F

static unsigned short *vga_buffer = (unsigned short *)VGA_ADDRESS;
static unsigned int screen_row = 0;
static unsigned int screen_col = 0;
static unsigned char screen_color = VGA_COLOR_DEFAULT;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (unsigned int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga_buffer[i] = (screen_color << 8) | ' ';
    }
    screen_row = 0;
    screen_col = 0;
}

void screen_putchar(char c, unsigned char color) {
    if (c == '\n') {
        screen_row++;
        screen_col = 0;
        if (screen_row >= VGA_HEIGHT) {
            screen_scroll();
        }
        return;
    }

    unsigned int index = screen_row * VGA_WIDTH + screen_col;
    vga_buffer[index] = (color << 8) | c;
    screen_col++;

    if (screen_col >= VGA_WIDTH) {
        screen_col = 0;
        screen_row++;
        if (screen_row >= VGA_HEIGHT) {
            screen_scroll();
        }
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
    screen_color = color;
}

int screen_get_row(void) {
    return screen_row;
}

void screen_scroll(void) {
    for (unsigned int y = 1; y < VGA_HEIGHT; y++) {
        for (unsigned int x = 0; x < VGA_WIDTH; x++) {
            unsigned int src = y * VGA_WIDTH + x;
            unsigned int dst = (y - 1) * VGA_WIDTH + x;
            vga_buffer[dst] = vga_buffer[src];
        }
    }

    for (unsigned int x = 0; x < VGA_WIDTH; x++) {
        unsigned int index = (VGA_HEIGHT - 1) * VGA_WIDTH + x;
        vga_buffer[index] = (screen_color << 8) | ' ';
    }

    screen_row = VGA_HEIGHT - 1;
    screen_col = 0;
}