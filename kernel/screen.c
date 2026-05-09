#include "drivers/screen.h"
#include "kernel/io.h"

#define VIDEO_MEMORY 0xB8000
#define MAX_ROWS 25
#define MAX_COLS 80
#define TAB_SIZE 4

static unsigned int screen_row = 0;
static unsigned int screen_col = 0;
static unsigned char screen_color = 0x0F;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    unsigned short *video_memory = (unsigned short *)VIDEO_MEMORY;
    for (int i = 0; i < MAX_ROWS * MAX_COLS; i++) {
        video_memory[i] = (screen_color << 8) | ' ';
    }
    screen_row = 0;
    screen_col = 0;
}

void screen_putchar(char c, unsigned char color) {
    unsigned short *video_memory = (unsigned short *)VIDEO_MEMORY;
    unsigned short attribute = color << 8;

    if (c == '\n') {
        screen_col = 0;
        screen_row++;
    } else if (c == '\t') {
        screen_col += TAB_SIZE - (screen_col % TAB_SIZE);
    } else {
        video_memory[screen_row * MAX_COLS + screen_col] = attribute | c;
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
    unsigned short *video_memory = (unsigned short *)VIDEO_MEMORY;
    for (int i = 0; i < (MAX_ROWS - 1) * MAX_COLS; i++) {
        video_memory[i] = video_memory[i + MAX_COLS];
    }

    for (int i = (MAX_ROWS - 1) * MAX_COLS; i < MAX_ROWS * MAX_COLS; i++) {
        video_memory[i] = (screen_color << 8) | ' ';
    }

    screen_row = MAX_ROWS - 1;
    screen_col = 0;
}