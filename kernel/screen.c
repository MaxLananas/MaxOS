#include "screen.h"
#include "io.h"

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY 0xB8000

unsigned char color = 0x0F;
unsigned int cursor_row = 0;
unsigned int cursor_col = 0;
unsigned short *vga_buffer = (unsigned short*)VGA_MEMORY;

void screen_init(void)
{
    screen_clear();
}

void screen_clear(void)
{
    for (unsigned int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga_buffer[i] = (unsigned char)' ' | (color << 8);
    }
    cursor_row = 0;
    cursor_col = 0;
}

void screen_putchar(char c, unsigned char col)
{
    if (c == '\n') {
        cursor_col = 0;
        cursor_row++;
    } else {
        unsigned int index = cursor_row * VGA_WIDTH + cursor_col;
        vga_buffer[index] = (col << 8) | (unsigned char)c;
        cursor_col++;
    }

    if (cursor_col >= VGA_WIDTH) {
        cursor_col = 0;
        cursor_row++;
    }

    if (cursor_row >= VGA_HEIGHT) {
        screen_scroll();
    }
}

void screen_write(const char *str, unsigned char col)
{
    while (*str) {
        screen_putchar(*str++, col);
    }
}

void screen_writeln(const char *str, unsigned char col)
{
    screen_write(str, col);
    screen_putchar('\n', col);
}

void screen_set_color(unsigned char col)
{
    color = col;
}

int screen_get_row(void)
{
    return cursor_row;
}

void screen_scroll(void)
{
    for (unsigned int i = 0; i < VGA_HEIGHT - 1; i++) {
        for (unsigned int j = 0; j < VGA_WIDTH; j++) {
            vga_buffer[i * VGA_WIDTH + j] = vga_buffer[(i + 1) * VGA_WIDTH + j];
        }
    }

    for (unsigned int j = 0; j < VGA_WIDTH; j++) {
        vga_buffer[(VGA_HEIGHT - 1) * VGA_WIDTH + j] = (color << 8) | (unsigned char)' ';
    }

    cursor_row = VGA_HEIGHT - 1;
}