#include "screen.h"
#include "io.h"

#define VIDEO_MEMORY 0xB8000
#define WIDTH 80
#define HEIGHT 25

unsigned char color = 0x0F;
unsigned short *video_memory = (unsigned short*)VIDEO_MEMORY;
unsigned int row = 0;
unsigned int col = 0;

void screen_init() {
    screen_clear();
}

void screen_clear() {
    for (unsigned int i = 0; i < WIDTH * HEIGHT; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    row = 0;
    col = 0;
}

void screen_putchar(char c, unsigned char new_color) {
    if (new_color != color) {
        color = new_color;
    }

    if (c == '\n') {
        col = 0;
        row++;
        if (row >= HEIGHT) {
            screen_scroll();
            row = HEIGHT - 1;
        }
        return;
    }

    video_memory[row * WIDTH + col] = (color << 8) | c;
    col++;

    if (col >= WIDTH) {
        col = 0;
        row++;
        if (row >= HEIGHT) {
            screen_scroll();
            row = HEIGHT - 1;
        }
    }
}

void screen_write(const char *str, unsigned char new_color) {
    while (*str) {
        screen_putchar(*str++, new_color);
    }
}

void screen_writeln(const char *str, unsigned char new_color) {
    screen_write(str, new_color);
    screen_putchar('\n', new_color);
}

void screen_set_color(unsigned char new_color) {
    color = new_color;
}

int screen_get_row() {
    return row;
}

void screen_scroll() {
    for (unsigned int i = 0; i < (HEIGHT - 1) * WIDTH; i++) {
        video_memory[i] = video_memory[i + WIDTH];
    }

    for (unsigned int i = (HEIGHT - 1) * WIDTH; i < HEIGHT * WIDTH; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    col = 0;
}