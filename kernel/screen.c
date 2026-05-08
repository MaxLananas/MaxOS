#include "drivers/screen.h"
#include "kernel/io.h"

#define VIDEO_MEMORY 0xB8000
#define MAX_ROWS 25
#define MAX_COLS 80
#define DEFAULT_COLOR 0x0F

typedef struct {
    unsigned char color;
    unsigned short *buffer;
    int row;
    int col;
} ScreenState;

static ScreenState screen = {DEFAULT_COLOR, (unsigned short*)VIDEO_MEMORY, 0, 0};

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    unsigned short *video_memory = (unsigned short*)VIDEO_MEMORY;
    for (int i = 0; i < MAX_ROWS * MAX_COLS; i++) {
        video_memory[i] = (DEFAULT_COLOR << 8) | ' ';
    }
    screen.row = 0;
    screen.col = 0;
}

void screen_putchar(char c, unsigned char color) {
    if (color != 0) screen.color = color;

    unsigned short *video_memory = (unsigned short*)VIDEO_MEMORY;
    unsigned short attribute = screen.color << 8;

    if (c == '\n') {
        screen.row++;
        screen.col = 0;
        if (screen.row >= MAX_ROWS) {
            screen_scroll();
            screen.row = MAX_ROWS - 1;
        }
        return;
    }

    video_memory[screen.row * MAX_COLS + screen.col] = attribute | c;
    screen.col++;

    if (screen.col >= MAX_COLS) {
        screen.col = 0;
        screen.row++;
        if (screen.row >= MAX_ROWS) {
            screen_scroll();
            screen.row = MAX_ROWS - 1;
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

void screen_set_color(unsigned char color) {
    screen.color = color;
}

int screen_get_row(void) {
    return screen.row;
}

void screen_scroll(void) {
    unsigned short *video_memory = (unsigned short*)VIDEO_MEMORY;
    for (int i = 0; i < (MAX_ROWS - 1) * MAX_COLS; i++) {
        video_memory[i] = video_memory[i + MAX_COLS];
    }
    for (int i = (MAX_ROWS - 1) * MAX_COLS; i < MAX_ROWS * MAX_COLS; i++) {
        video_memory[i] = (DEFAULT_COLOR << 8) | ' ';
    }
    if (screen.row > 0) screen.row--;
}