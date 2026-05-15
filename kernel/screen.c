#include "screen.h"
#include "io.h"

#define VIDEO_MEMORY 0xB8000
#define WIDTH 80
#define HEIGHT 25

unsigned char color = 0x0F;
unsigned int cursor_pos = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    unsigned short *video_memory = (unsigned short*)VIDEO_MEMORY;
    for (int i = 0; i < WIDTH * HEIGHT; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    cursor_pos = 0;
}

void screen_putchar(char c, unsigned char color) {
    unsigned short *video_memory = (unsigned short*)VIDEO_MEMORY;

    if (c == '\n') {
        cursor_pos += WIDTH - (cursor_pos % WIDTH);
    } else if (c == '\b') {
        if (cursor_pos > 0) cursor_pos--;
        video_memory[cursor_pos] = (color << 8) | ' ';
    } else {
        video_memory[cursor_pos] = (color << 8) | c;
        cursor_pos++;
    }

    if (cursor_pos >= WIDTH * HEIGHT) {
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

void screen_set_color(unsigned char color) {
    screen_color = color;
}

int screen_get_row(void) {
    return cursor_pos / WIDTH;
}

void screen_scroll(void) {
    unsigned short *video_memory = (unsigned short*)VIDEO_MEMORY;
    for (int i = 0; i < WIDTH * (HEIGHT - 1); i++) {
        video_memory[i] = video_memory[i + WIDTH];
    }
    for (int i = WIDTH * (HEIGHT - 1); i < WIDTH * HEIGHT; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    cursor_pos -= WIDTH;
}