#include "screen.h"
#include "io.h"

#define VIDEO_MEMORY 0xB8000
#define SCREEN_WIDTH 80
#define SCREEN_HEIGHT 25
#define DEFAULT_COLOR 0x0F

static unsigned char color = DEFAULT_COLOR;
static unsigned int row = 0;
static unsigned int col = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    unsigned short *video = (unsigned short*)VIDEO_MEMORY;
    for (unsigned int i = 0; i < SCREEN_WIDTH * SCREEN_HEIGHT; i++) {
        video[i] = (color << 8) | ' ';
    }
    row = 0;
    col = 0;
}

void screen_putchar(char c, unsigned char c_color) {
    if (c == '\n') {
        col = 0;
        row++;
    } else {
        unsigned short *video = (unsigned short*)VIDEO_MEMORY;
        video[row * SCREEN_WIDTH + col] = (c_color << 8) | c;
        col++;
        if (col >= SCREEN_WIDTH) {
            col = 0;
            row++;
        }
    }
    if (row >= SCREEN_HEIGHT) {
        screen_scroll();
    }
}

void screen_write(const char *str, unsigned char c_color) {
    while (*str) {
        screen_putchar(*str++, c_color);
    }
}

void screen_writeln(const char *str, unsigned char c_color) {
    screen_write(str, c_color);
    screen_putchar('\n', c_color);
}

void screen_set_color(unsigned char c_color) {
    color = c_color;
}

int screen_get_row(void) {
    return row;
}

void screen_scroll(void) {
    unsigned short *video = (unsigned short*)VIDEO_MEMORY;
    for (unsigned int i = 0; i < SCREEN_WIDTH * (SCREEN_HEIGHT - 1); i++) {
        video[i] = video[i + SCREEN_WIDTH];
    }
    for (unsigned int i = SCREEN_WIDTH * (SCREEN_HEIGHT - 1); i < SCREEN_WIDTH * SCREEN_HEIGHT; i++) {
        video[i] = (color << 8) | ' ';
    }
    row = SCREEN_HEIGHT - 1;
}