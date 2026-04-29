#include "screen.h"
#include "io.h"

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY 0xB8000

static unsigned char color = 0x0F;
static unsigned short *video_memory = (unsigned short*)VGA_MEMORY;
static unsigned int row = 0;
static unsigned int col = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    row = 0;
    col = 0;
}

void screen_putchar(char c, unsigned char color) {
    if (c == '\n') {
        col = 0;
        row++;
    } else {
        video_memory[row * VGA_WIDTH + col] = (color << 8) | c;
        col++;
        if (col >= VGA_WIDTH) {
            col = 0;
            row++;
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
    for (int i = 0; i < VGA_HEIGHT - 1; i++) {
        for (int j = 0; j < VGA_WIDTH; j++) {
            video_memory[i * VGA_WIDTH + j] = video_memory[(i + 1) * VGA_WIDTH + j];
        }
    }

    for (int j = 0; j < VGA_WIDTH; j++) {
        video_memory[(VGA_HEIGHT - 1) * VGA_WIDTH + j] = (color << 8) | ' ';
    }

    row = VGA_HEIGHT - 1;
    col = 0;
}