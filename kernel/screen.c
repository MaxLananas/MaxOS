#include "screen.h"
#include "io.h"

#define VIDEO_MEMORY 0xB8000
#define WIDTH 80
#define HEIGHT 25

static unsigned char color = 0x0F;
static unsigned short *video_memory = (unsigned short*)VIDEO_MEMORY;
static int row = 0;
static int col = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (int i = 0; i < WIDTH * HEIGHT; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    row = 0;
    col = 0;
}

void screen_putchar(char c, unsigned char color) {
    if (c == '\n') {
        col = 0;
        row++;
    } else if (c == '\b') {
        if (col > 0) col--;
        video_memory[row * WIDTH + col] = (color << 8) | ' ';
    } else {
        video_memory[row * WIDTH + col] = (color << 8) | c;
        col++;
    }

    if (col >= WIDTH) {
        col = 0;
        row++;
    }

    if (row >= HEIGHT) {
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

void screen_set_color(unsigned char c) {
    color = c;
}

int screen_get_row(void) {
    return row;
}

void screen_scroll(void) {
    for (int i = 0; i < (HEIGHT - 1) * WIDTH; i++) {
        video_memory[i] = video_memory[i + WIDTH];
    }

    for (int i = (HEIGHT - 1) * WIDTH; i < HEIGHT * WIDTH; i++) {
        video_memory[i] = (color << 8) | ' ';
    }

    row = HEIGHT - 1;
    col = 0;
}