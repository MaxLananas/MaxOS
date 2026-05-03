#include "screen.h"
#include "io.h"

#define VIDEO_MEMORY 0xB8000
#define MAX_ROWS 25
#define MAX_COLS 80

unsigned char color = 0x07;
unsigned short *video_memory = (unsigned short*)VIDEO_MEMORY;
unsigned int cursor_row = 0;
unsigned int cursor_col = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (unsigned int i = 0; i < MAX_ROWS * MAX_COLS; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    cursor_row = 0;
    cursor_col = 0;
}

void screen_putchar(char c, unsigned char col) {
    if (c == '\n') {
        cursor_col = 0;
        cursor_row++;
    } else if (c == '\r') {
        cursor_col = 0;
    } else if (c == '\b') {
        if (cursor_col > 0) cursor_col--;
        video_memory[cursor_row * MAX_COLS + cursor_col] = (col << 8) | ' ';
    } else {
        video_memory[cursor_row * MAX_COLS + cursor_col] = (col << 8) | c;
        cursor_col++;
    }

    if (cursor_col >= MAX_COLS) {
        cursor_col = 0;
        cursor_row++;
    }

    if (cursor_row >= MAX_ROWS) {
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

int screen_get_row(void) {
    return cursor_row;
}

void screen_scroll(void) {
    for (unsigned int i = 1; i < MAX_ROWS; i++) {
        for (unsigned int j = 0; j < MAX_COLS; j++) {
            video_memory[(i-1) * MAX_COLS + j] = video_memory[i * MAX_COLS + j];
        }
    }

    for (unsigned int j = 0; j < MAX_COLS; j++) {
        video_memory[(MAX_ROWS-1) * MAX_COLS + j] = (color << 8) | ' ';
    }

    cursor_row--;
}