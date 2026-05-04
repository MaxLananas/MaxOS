#include "screen.h"
#include "../kernel/io.h"

#define VIDEO_MEMORY 0xB8000
#define MAX_ROWS 25
#define MAX_COLS 80
#define SCREEN_SIZE (MAX_ROWS * MAX_COLS)

static unsigned char color = 0x0F;
static unsigned int row = 0;
static unsigned int col = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    unsigned short *video_memory = (unsigned short *)VIDEO_MEMORY;
    for (int i = 0; i < SCREEN_SIZE; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    row = 0;
    col = 0;
}

void screen_putchar(char c, unsigned char color) {
    unsigned short *video_memory = (unsigned short *)VIDEO_MEMORY;

    if (c == '\n') {
        col = 0;
        row++;
    } else {
        video_memory[row * MAX_COLS + col] = (color << 8) | c;
        col++;
        if (col >= MAX_COLS) {
            col = 0;
            row++;
        }
    }

    if (row >= MAX_ROWS) {
        screen_scroll();
    }
}

void screen_write(const char *str, unsigned char color) {
    while (*str) {
        screen_putchar(*str, color);
        str++;
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
    unsigned short *video_memory = (unsigned short *)VIDEO_MEMORY;

    for (int i = 0; i < (MAX_ROWS - 1) * MAX_COLS; i++) {
        video_memory[i] = video_memory[i + MAX_COLS];
    }

    for (int i = (MAX_ROWS - 1) * MAX_COLS; i < MAX_ROWS * MAX_COLS; i++) {
        video_memory[i] = (color << 8) | ' ';
    }

    row = MAX_ROWS - 1;
}