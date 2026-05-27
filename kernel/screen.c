#include "io.h"
#include "screen.h"

static unsigned char *video_memory = (unsigned char*)0xB8000;
static unsigned int cursor_x = 0;
static unsigned int cursor_y = 0;
static unsigned char color = 0x0F;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (int i = 0; i < 80 * 25 * 2; i += 2) {
        video_memory[i] = ' ';
        video_memory[i + 1] = color;
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

void screen_write(const char *str, unsigned char color) {
    for (int i = 0; str[i] != '\0'; i++) {
        screen_putchar(str[i], color);
    }
}

void screen_writeln(const char *str, unsigned char color) {
    screen_write(str, color);
    screen_putchar('\n', color);
}

void screen_set_color(unsigned char col) {
    color = col;
}

int screen_get_row(void) {
    return cursor_y;
}

void screen_scroll(void) {
    for (int y = 1; y < 25; y++) {
        for (int x = 0; x < 80; x++) {
            video_memory[((y - 1) * 80 + x) * 2] = video_memory[(y * 80 + x) * 2];
            video_memory[((y - 1) * 80 + x) * 2 + 1] = video_memory[(y * 80 + x) * 2 + 1];
        }
    }

    for (int x = 0; x < 80; x++) {
        video_memory[(24 * 80 + x) * 2] = ' ';
        video_memory[(24 * 80 + x) * 2 + 1] = color;
    }

    cursor_y = 24;
}