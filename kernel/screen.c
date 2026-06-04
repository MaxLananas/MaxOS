#include "screen.h"
#include "io.h"

unsigned short *video_memory = (unsigned short*)0xB8000;
unsigned char color = 0x0F;
unsigned int cursor_row = 0;
unsigned int cursor_col = 0;

void screen_init(void)
{
    screen_clear();
}

void screen_clear(void)
{
    for (unsigned int i = 0; i < 80 * 25; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    cursor_row = 0;
    cursor_col = 0;
}

void screen_putchar(char c, unsigned char color)
{
    if (c == '\n') {
        cursor_col = 0;
        cursor_row++;
    } else {
        video_memory[cursor_row * 80 + cursor_col] = (color << 8) | c;
        cursor_col++;
    }

    if (cursor_col >= 80) {
        cursor_col = 0;
        cursor_row++;
    }

    if (cursor_row >= 25) {
        screen_scroll();
    }
}

void screen_write(const char *str, unsigned char color)
{
    while (*str) {
        screen_putchar(*str++, color);
    }
}

void screen_writeln(const char *str, unsigned char color)
{
    screen_write(str, color);
    screen_putchar('\n', color);
}

void screen_set_color(unsigned char color)
{
    screen_color = color;
}

int screen_get_row(void)
{
    return cursor_row;
}

void screen_scroll(void)
{
    for (unsigned int i = 0; i < 24 * 80; i++) {
        video_memory[i] = video_memory[i + 80];
    }

    for (unsigned int i = 24 * 80; i < 25 * 80; i++) {
        video_memory[i] = (color << 8) | ' ';
    }

    cursor_row = 24;
}