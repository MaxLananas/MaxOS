#include "io.h"
#include "screen.h"

static unsigned short *video_memory = (unsigned short *)0xB8000;
static unsigned char color = 0x0F;
static int row = 0;
static int col = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (int i = 0; i < 80 * 25; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    row = 0;
    col = 0;
}

void screen_putchar(char c, unsigned char col) {
    if (c == '\n') {
        row++;
        col = 0;
    } else {
        video_memory[row * 80 + col] = (col << 8) | c;
        col++;
    }

    if (col >= 80) {
        col = 0;
        row++;
    }

    if (row >= 25) {
        screen_scroll();
    }
}

void screen_write(const char *str, unsigned char col) {
    for (int i = 0; str[i]; i++) {
        screen_putchar(str[i], col);
    }
}

void screen_writeln(const char *str, unsigned char col) {
    screen_write(str, col);
    screen_putchar('\n', col);
}

void screen_set_color(unsigned char col) {
    color = col;
}

int screen_get_row(void) {
    return row;
}

void screen_scroll(void) {
    for (int i = 0; i < 24 * 80; i++) {
        video_memory[i] = video_memory[i + 80];
    }
    for (int i = 24 * 80; i < 25 * 80; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    row = 24;
}