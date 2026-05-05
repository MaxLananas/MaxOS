#include "../drivers/screen.h"
#include "../kernel/io.h"

static unsigned short *video_memory = (unsigned short*)0xB8000;
static unsigned char current_color = 0x0F;
static int cursor_x = 0;
static int cursor_y = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (int i = 0; i < 80 * 25; i++) {
        video_memory[i] = (current_color << 8) | ' ';
    }
    cursor_x = 0;
    cursor_y = 0;
}

void screen_putchar(char c, unsigned char color) {
    if (c == '\n') {
        cursor_y++;
        cursor_x = 0;
    } else {
        video_memory[cursor_y * 80 + cursor_x] = (color << 8) | c;
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
    for (int i = 0; str[i] != 0; i++) {
        screen_putchar(str[i], color);
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
    return cursor_y;
}

void screen_scroll(void) {
    for (int y = 1; y < 25; y++) {
        for (int x = 0; x < 80; x++) {
            video_memory[(y-1)*80 + x] = video_memory[y*80 + x];
        }
    }

    for (int x = 0; x < 80; x++) {
        video_memory[24*80 + x] = (current_color << 8) | ' ';
    }

    cursor_y = 24;
}