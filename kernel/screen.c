#include "screen.h"
#include "io.h"

#define VIDEO_MEMORY 0xB8000
#define MAX_ROWS 25
#define MAX_COLS 80

unsigned char color = 0x0F;
unsigned short *video_memory = (unsigned short *)VIDEO_MEMORY;
int row = 0;
int col = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    unsigned short blank = 0x20 | (color << 8);

    for (int i = 0; i < MAX_ROWS * MAX_COLS; i++) {
        video_memory[i] = blank;
    }

    row = 0;
    col = 0;
}

void screen_putchar(char c, unsigned char color) {
    if (c == '\n') {
        row++;
        col = 0;
        return;
    }

    unsigned short *location = video_memory + (row * MAX_COLS + col);
    *location = c | (color << 8);
    col++;

    if (col >= MAX_COLS) {
        row++;
        col = 0;
    }

    if (row >= MAX_ROWS) {
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
    for (int i = 0; i < (MAX_ROWS - 1) * MAX_COLS; i++) {
        video_memory[i] = video_memory[i + MAX_COLS];
    }

    unsigned short blank = 0x20 | (color << 8);
    for (int i = (MAX_ROWS - 1) * MAX_COLS; i < MAX_ROWS * MAX_COLS; i++) {
        video_memory[i] = blank;
    }

    row = MAX_ROWS - 1;
}