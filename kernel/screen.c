#include "screen.h"
#include "io.h"

#define VIDEO_MEMORY 0xB8000
#define WIDTH 80
#define HEIGHT 25

unsigned char color = 0x0F;
unsigned int row = 0;
unsigned int col = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    unsigned short *video = (unsigned short*)VIDEO_MEMORY;
    for (int i = 0; i < WIDTH * HEIGHT; i++) {
        video[i] = (color << 8) | ' ';
    }
    row = 0;
    col = 0;
}

void screen_putchar(char c, unsigned char color) {
    unsigned short *video = (unsigned short*)VIDEO_MEMORY;
    unsigned short attrib = color << 8;

    if (c == '\n') {
        col = 0;
        row++;
        if (row >= HEIGHT) {
            screen_scroll();
            row = HEIGHT - 1;
        }
    } else {
        video[row * WIDTH + col] = attrib | c;
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
    unsigned short *video = (unsigned short*)VIDEO_MEMORY;
    for (int i = 0; i < (HEIGHT - 1) * WIDTH; i++) {
        video[i] = video[i + WIDTH];
    }
    for (int i = (HEIGHT - 1) * WIDTH; i < HEIGHT * WIDTH; i++) {
        video[i] = (color << 8) | ' ';
    }
    if (row > 0) row--;
}