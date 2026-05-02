#include "screen.h"
#include "io.h"

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
    unsigned short *video = (unsigned short*)VIDEO_MEMORY;
    for (unsigned int i = 0; i < SCREEN_SIZE; i++) {
        video[i] = (color << 8) | ' ';
    }
    row = 0;
    col = 0;
}

void screen_putchar(char c, unsigned char clr) {
    unsigned short *video = (unsigned short*)VIDEO_MEMORY;
    if (c == '\n') {
        col = 0;
        row++;
    } else {
        video[row * MAX_COLS + col] = (clr << 8) | c;
        col++;
        if (col >= MAX_COLS) {
            col = 0;
            row++;
        }
    }
    if (row >= MAX_ROWS) {
        screen_scroll();
        row = MAX_ROWS - 1;
    }
}

void screen_write(const char *str, unsigned char clr) {
    while (*str) {
        screen_putchar(*str++, clr);
    }
}

void screen_writeln(const char *str, unsigned char clr) {
    screen_write(str, clr);
    screen_putchar('\n', clr);
}

void screen_set_color(unsigned char clr) {
    color = clr;
}

int screen_get_row(void) {
    return row;
}

void screen_scroll(void) {
    unsigned short *video = (unsigned short*)VIDEO_MEMORY;
    for (unsigned int i = 0; i < (MAX_ROWS - 1) * MAX_COLS; i++) {
        video[i] = video[i + MAX_COLS];
    }
    for (unsigned int i = (MAX_ROWS - 1) * MAX_COLS; i < SCREEN_SIZE; i++) {
        video[i] = (color << 8) | ' ';
    }
}