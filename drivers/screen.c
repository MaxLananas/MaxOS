#include "kernel/io.h"

#define VIDEO_MEMORY 0xB8000
#define MAX_ROWS 25
#define MAX_COLS 80
#define TAB_SIZE 4

static unsigned char color = 0x0F;
static unsigned int row = 0;
static unsigned int col = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    unsigned short *video = (unsigned short*)VIDEO_MEMORY;
    for (int i = 0; i < MAX_ROWS * MAX_COLS; i++) {
        video[i] = (color << 8) | ' ';
    }
    row = 0;
    col = 0;
}

void screen_putchar(char c, unsigned char color) {
    unsigned short *video = (unsigned short*)VIDEO_MEMORY;
    unsigned short attrib = color << 8;

    if (c == '\n') {
        row++;
        col = 0;
        if (row >= MAX_ROWS) {
            screen_scroll();
            row = MAX_ROWS - 1;
        }
    } else if (c == '\t') {
        for (int i = 0; i < TAB_SIZE; i++) {
            screen_putchar(' ', color);
        }
    } else {
        video[row * MAX_COLS + col] = attrib | c;
        col++;
        if (col >= MAX_COLS) {
            row++;
            col = 0;
            if (row >= MAX_ROWS) {
                screen_scroll();
                row = MAX_ROWS - 1;
            }
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

void screen_set_color(unsigned char new_color) {
    color = new_color;
}

int screen_get_row(void) {
    return row;
}

void screen_scroll(void) {
    unsigned short *video = (unsigned short*)VIDEO_MEMORY;
    for (int i = 0; i < (MAX_ROWS - 1) * MAX_COLS; i++) {
        video[i] = video[i + MAX_COLS];
    }
    for (int i = (MAX_ROWS - 1) * MAX_COLS; i < MAX_ROWS * MAX_COLS; i++) {
        video[i] = (color << 8) | ' ';
    }
    if (row > 0) row--;
}