#include "screen.h"
#include "io.h"

static unsigned char color = 0x0F;
static unsigned short *video_memory = (unsigned short *)0xB8000;
static unsigned int row = 0;
static unsigned int col = 0;

void screen_init(void)
{
    screen_clear();
}

void screen_clear(void)
{
    for (unsigned int i = 0; i < 80 * 25; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    row = 0;
    col = 0;
}

void screen_putchar(char c, unsigned char color)
{
    if (c == '\n') {
        row++;
        col = 0;
        return;
    }

    video_memory[row * 80 + col] = (color << 8) | c;
    col++;

    if (col >= 80) {
        row++;
        col = 0;
    }

    if (row >= 25) {
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

void screen_set_color(unsigned char new_color)
{
    color = new_color;
}

int screen_get_row(void)
{
    return row;
}

void screen_scroll(void)
{
    for (unsigned int i = 0; i < 24 * 80; i++) {
        video_memory[i] = video_memory[i + 80];
    }

    for (unsigned int i = 24 * 80; i < 25 * 80; i++) {
        video_memory[i] = (color << 8) | ' ';
    }

    row = 24;
    col = 0;
}