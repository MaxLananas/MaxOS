#include "screen.h"
#include "io.h"

static unsigned short *video_memory = (unsigned short*)0xB8000;
static unsigned char current_color = 0x07;
static int current_row = 0;
static int current_col = 0;

void screen_init(void) {
    video_memory = (unsigned short*)0xB8000;
    current_row = 0;
    current_col = 0;
    current_color = 0x07;
    screen_clear();
}

void screen_clear(void) {
    unsigned int i;
    for (i = 0; i < 80 * 25; i++) {
        video_memory[i] = (current_color << 8) | ' ';
    }
    current_row = 0;
    current_col = 0;
}

void screen_putchar(char c, unsigned char color) {
    if (c == '\n') {
        current_row++;
        current_col = 0;
        if (current_row >= 25) {
            screen_scroll();
            current_row = 24;
        }
        return;
    }

    if (c == '\t') {
        current_col += 4 - (current_col % 4);
        if (current_col >= 80) {
            current_col = 0;
            current_row++;
            if (current_row >= 25) {
                screen_scroll();
                current_row = 24;
            }
        }
        return;
    }

    video_memory[current_row * 80 + current_col] = (color << 8) | c;
    current_col++;
    if (current_col >= 80) {
        current_col = 0;
        current_row++;
        if (current_row >= 25) {
            screen_scroll();
            current_row = 24;
        }
    }
}

void screen_write(const char *str, unsigned char color) {
    unsigned int i = 0;
    while (str[i] != 0) {
        screen_putchar(str[i], color);
        i++;
    }
}

void screen_writeln(const char *str, unsigned char color) {
    screen_write(str, color);
    screen_putchar('\n', color);
}

void screen_set_color(unsigned char color) {
    current_color = color;
}

int screen_get_row(void) {
    return current_row;
}

void screen_scroll(void) {
    unsigned int i;
    for (i = 0; i < 24 * 80; i++) {
        video_memory[i] = video_memory[i + 80];
    }
    for (i = 24 * 80; i < 25 * 80; i++) {
        video_memory[i] = (current_color << 8) | ' ';
    }
}