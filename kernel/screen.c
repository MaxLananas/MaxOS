#include "screen.h"
#include "io.h"

#define VIDEO_MEMORY 0xB8000
#define MAX_ROWS 25
#define MAX_COLS 80

static unsigned char color = 0x0F;
static unsigned short *video_memory = (unsigned short*)VIDEO_MEMORY;
static unsigned int row = 0;
static unsigned int col = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (unsigned int i = 0; i < MAX_ROWS * MAX_COLS; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    row = 0;
    col = 0;
}

void screen_putchar(char c, unsigned char color) {
    if (c == '\n') {
        row++;
        col = 0;
        if (row >= MAX_ROWS) {
            screen_scroll();
        }
        return;
    }
    if (col >= MAX_COLS) {
        row++;
        col = 0;
        if (row >= MAX_ROWS) {
            screen_scroll();
        }
    }
    video_memory[row * MAX_COLS + col] = (color << 8) | c;
    col++;
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

void screen_set_color(unsigned char c) {
    color = c;
}

int screen_get_row(void) {
    return row;
}

void screen_scroll(void) {
    for (unsigned int i = 0; i < MAX_ROWS - 1; i++) {
        for (unsigned int j = 0; j < MAX_COLS; j++) {
            video_memory[i * MAX_COLS + j] = video_memory[(i + 1) * MAX_COLS + j];
        }
    }
    for (unsigned int j = 0; j < MAX_COLS; j++) {
        video_memory[(MAX_ROWS - 1) * MAX_COLS + j] = (color << 8) | ' ';
    }
    row--;
}