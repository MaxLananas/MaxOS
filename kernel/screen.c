#include "screen.h"
#include "io.h"

static volatile unsigned char *video_memory = (unsigned char*)0xB8000;
static unsigned int cursor_x = 0;
static unsigned int cursor_y = 0;
static unsigned char current_color = 0x07;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (unsigned int i = 0; i < 80 * 25 * 2; i += 2) {
        video_memory[i] = ' ';
        video_memory[i+1] = current_color;
    }
    cursor_x = 0;
    cursor_y = 0;
    move_cursor();
}

void screen_putchar(char c, unsigned char color) {
    if (c == '\n') {
        cursor_x = 0;
        cursor_y++;
    } else {
        unsigned int index = (cursor_y * 80 + cursor_x) * 2;
        video_memory[index] = c;
        video_memory[index+1] = color;
        cursor_x++;
    }

    if (cursor_x >= 80) {
        cursor_x = 0;
        cursor_y++;
    }

    if (cursor_y >= 25) {
        screen_scroll();
    }

    move_cursor();
}

void screen_write(const char *str, unsigned char color) {
    for (unsigned int i = 0; str[i] != '\0'; i++) {
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
    for (unsigned int y = 1; y < 25; y++) {
        for (unsigned int x = 0; x < 80; x++) {
            unsigned int src = (y * 80 + x) * 2;
            unsigned int dst = ((y-1) * 80 + x) * 2;
            video_memory[dst] = video_memory[src];
            video_memory[dst+1] = video_memory[src+1];
        }
    }

    for (unsigned int x = 0; x < 80; x++) {
        unsigned int index = (24 * 80 + x) * 2;
        video_memory[index] = ' ';
        video_memory[index+1] = current_color;
    }

    cursor_y = 24;
    move_cursor();
}

static void move_cursor(void) {
    unsigned short position = cursor_y * 80 + cursor_x;
    outb(0x3D4, 0x0F);
    outb(0x3D5, (unsigned char)(position & 0xFF));
    outb(0x3D4, 0x0E);
    outb(0x3D5, (unsigned char)((position >> 8) & 0xFF));
}