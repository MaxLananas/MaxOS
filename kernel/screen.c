#include "io.h"
#include "screen.h"

static unsigned int cursor_x = 0;
static unsigned int cursor_y = 0;
static unsigned char color = 0x0F;
static unsigned char *video_memory = (unsigned char*)0xB8000;

void screen_init(void) {
    cursor_x = 0;
    cursor_y = 0;
    color = 0x0F;
}

void screen_clear(void) {
    unsigned int i;
    for (i = 0; i < 80 * 25 * 2; i += 2) {
        video_memory[i] = ' ';
        video_memory[i+1] = color;
    }
    cursor_x = 0;
    cursor_y = 0;
}

void screen_putchar(char c, unsigned char col) {
    if (c == '\n') {
        cursor_x = 0;
        cursor_y++;
    } else {
        video_memory[(cursor_y * 80 + cursor_x) * 2] = c;
        video_memory[(cursor_y * 80 + cursor_x) * 2 + 1] = col;
        cursor_x++;
    }

    if (cursor_x >= 80) {
        cursor_x = 0;
        cursor_y++;
    }

    if (cursor_y >= 25) {
        screen_scroll();
    }
}

void screen_write(const char *str, unsigned char col) {
    unsigned int i = 0;
    while (str[i]) {
        screen_putchar(str[i], col);
        i++;
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
    return cursor_y;
}

void screen_scroll(void) {
    unsigned int i;
    for (i = 0; i < 24 * 80 * 2; i++) {
        video_memory[i] = video_memory[i + 80 * 2];
    }
    for (i = 24 * 80 * 2; i < 25 * 80 * 2; i += 2) {
        video_memory[i] = ' ';
        video_memory[i+1] = color;
    }
    cursor_y = 24;
}