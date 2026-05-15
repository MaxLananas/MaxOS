#include "drivers/screen.h"
#include "kernel/io.h"

#define VIDEO_MEMORY 0xB8000
#define MAX_ROWS 25
#define MAX_COLS 80

unsigned char screen_color = 0x0F; // Default white on black
unsigned char *screen_buffer = (unsigned char *)VIDEO_MEMORY;
int screen_row = 0;
int screen_col = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (int i = 0; i < MAX_ROWS * MAX_COLS * 2; i += 2) {
        screen_buffer[i] = ' ';
        screen_buffer[i + 1] = screen_color;
    }
    screen_row = 0;
    screen_col = 0;
}

void screen_putchar(char c, unsigned char color) {
    if (color != 0) screen_color = color;

    if (c == '\n') {
        screen_col = 0;
        screen_row++;
    } else {
        unsigned short pos = (screen_row * MAX_COLS + screen_col) * 2;
        screen_buffer[pos] = c;
        screen_buffer[pos + 1] = screen_color;
        screen_col++;
    }

    if (screen_col >= MAX_COLS) {
        screen_col = 0;
        screen_row++;
    }

    if (screen_row >= MAX_ROWS) {
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
    return screen_row;
}

void screen_scroll(void) {
    for (int i = 0; i < (MAX_ROWS - 1) * MAX_COLS * 2; i++) {
        screen_buffer[i] = screen_buffer[i + MAX_COLS * 2];
    }

    for (int i = (MAX_ROWS - 1) * MAX_COLS * 2; i < MAX_ROWS * MAX_COLS * 2; i += 2) {
        screen_buffer[i] = ' ';
        screen_buffer[i + 1] = screen_color;
    }

    screen_row = MAX_ROWS - 1;
    screen_col = 0;
}