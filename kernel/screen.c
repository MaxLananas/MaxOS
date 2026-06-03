#include "screen.h"
#include "io.h"

#define VIDEO_MEMORY 0xB8000
#define COLUMNS 80
#define ROWS 25
#define DEFAULT_COLOR 0x0F

unsigned char color = DEFAULT_COLOR;
unsigned short *video_memory = (unsigned short *)VIDEO_MEMORY;
int row = 0;
int column = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (int i = 0; i < COLUMNS * ROWS; i++) {
        video_memory[i] = (DEFAULT_COLOR << 8) | ' ';
    }
    row = 0;
    column = 0;
}

void screen_putchar(char c, unsigned char color) {
    if (c == '\n') {
        row++;
        column = 0;
    } else {
        video_memory[row * COLUMNS + column] = (color << 8) | c;
        column++;
        if (column >= COLUMNS) {
            row++;
            column = 0;
        }
    }
    if (row >= ROWS) {
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
    for (int i = 0; i < ROWS - 1; i++) {
        for (int j = 0; j < COLUMNS; j++) {
            video_memory[i * COLUMNS + j] = video_memory[(i + 1) * COLUMNS + j];
        }
    }
    for (int j = 0; j < COLUMNS; j++) {
        video_memory[(ROWS - 1) * COLUMNS + j] = (color << 8) | ' ';
    }
    row = ROWS - 1;
}