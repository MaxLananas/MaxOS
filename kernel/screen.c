#include "screen.h"
#include "io.h"

#define VIDEO_MEMORY 0xB8000
#define WIDTH 80
#define HEIGHT 25

static unsigned char color = 0x0F;
static unsigned int cursor = 0;

void screen_init() {
    screen_clear();
}

void screen_clear() {
    unsigned short *video = (unsigned short*)VIDEO_MEMORY;
    for (int i = 0; i < WIDTH * HEIGHT; i++) {
        video[i] = (color << 8) | ' ';
    }
    cursor = 0;
}

void screen_putchar(char c, unsigned char col) {
    unsigned short *video = (unsigned short*)VIDEO_MEMORY;
    if (c == '\n') {
        cursor += WIDTH - (cursor % WIDTH);
    } else {
        video[cursor++] = (col << 8) | c;
    }
    if (cursor >= WIDTH * HEIGHT) {
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

int screen_get_row() {
    return cursor / WIDTH;
}

void screen_scroll() {
    unsigned short *video = (unsigned short*)VIDEO_MEMORY;
    for (int i = 0; i < WIDTH * (HEIGHT - 1); i++) {
        video[i] = video[i + WIDTH];
    }
    for (int i = WIDTH * (HEIGHT - 1); i < WIDTH * HEIGHT; i++) {
        video[i] = (color << 8) | ' ';
    }
    cursor -= WIDTH;
}