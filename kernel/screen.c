#include "kernel/screen.h"
#include "kernel/io.h"

unsigned char color = 0x0F;
unsigned short *video_memory = (unsigned short*)0xB8000;
unsigned int row = 0;
unsigned int column = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (int i = 0; i < 80 * 25; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    row = 0;
    column = 0;
}

void screen_putchar(char c, unsigned char color) {
    if (c == '\n') {
        row++;
        column = 0;
    } else {
        video_memory[row * 80 + column] = (color << 8) | c;
        column++;
        if (column >= 80) {
            row++;
            column = 0;
        }
    }
    if (row >= 25) {
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
    screen_color = color;
}

int screen_get_row(void) {
    return row;
}

void screen_scroll(void) {
    for (int i = 0; i < 24 * 80; i++) {
        video_memory[i] = video_memory[i + 80];
    }
    for (int i = 24 * 80; i < 25 * 80; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    row = 24;
}