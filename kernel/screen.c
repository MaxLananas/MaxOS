#include "screen.h"
#include "io.h"

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY 0xB8000

unsigned char color = 0x0F;
unsigned short *video_memory = (unsigned short*)VGA_MEMORY;
int row = 0;
int column = 0;

void screen_init() {
    screen_clear();
}

void screen_clear() {
    for (int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    row = 0;
    column = 0;
}

void screen_putchar(char c, unsigned char col) {
    if (c == '\n') {
        row++;
        column = 0;
    } else {
        video_memory[row * VGA_WIDTH + column] = (col << 8) | c;
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

void screen_write(const char *str, unsigned char col) {
    while (*str) {
        screen_putchar(*str++, col);
    }
}

void screen_writeln(const char *str, unsigned char col) {
    screen_write(str, col);
    screen_putchar('\n', col);
}

void screen_set_color(unsigned char col) {
    color = col;
}

int screen_get_row() {
    return row;
}

void screen_scroll() {
    for (int i = 0; i < VGA_HEIGHT - 1; i++) {
        for (int j = 0; j < VGA_WIDTH; j++) {
            video_memory[i * VGA_WIDTH + j] = video_memory[(i + 1) * VGA_WIDTH + j];
        }
    }
    for (int j = 0; j < VGA_WIDTH; j++) {
        video_memory[(VGA_HEIGHT - 1) * VGA_WIDTH + j] = (color << 8) | ' ';
    }
    row = VGA_HEIGHT - 1;
}