#include "screen.h"
#include "io.h"

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY 0xB8000

static unsigned int row = 0;
static unsigned int column = 0;
static unsigned char color = 0x0F;

void screen_init(void) {
    row = 0;
    column = 0;
    color = 0x0F;
}

void screen_clear(void) {
    unsigned short *video_memory = (unsigned short *)VGA_MEMORY;

    for (unsigned int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        video_memory[i] = (color << 8) | ' ';
    }

    row = 0;
    column = 0;
}

void screen_putchar(char c, unsigned char color) {
    unsigned short *video_memory = (unsigned short *)VGA_MEMORY;

    if (c == '\n') {
        row++;
        column = 0;
        if (row >= VGA_HEIGHT) {
            screen_scroll();
        }
        return;
    }

    video_memory[row * VGA_WIDTH + column] = (color << 8) | c;
    column++;

    if (column >= VGA_WIDTH) {
        row++;
        column = 0;
        if (row >= VGA_HEIGHT) {
            screen_scroll();
        }
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

void screen_set_color(unsigned char new_color) {
    color = new_color;
}

int screen_get_row(void) {
    return row;
}

void screen_scroll(void) {
    unsigned short *video_memory = (unsigned short *)VGA_MEMORY;

    for (unsigned int i = 0; i < VGA_WIDTH * (VGA_HEIGHT - 1); i++) {
        video_memory[i] = video_memory[i + VGA_WIDTH];
    }

    for (unsigned int i = VGA_WIDTH * (VGA_HEIGHT - 1); i < VGA_WIDTH * VGA_HEIGHT; i++) {
        video_memory[i] = (color << 8) | ' ';
    }

    row = VGA_HEIGHT - 1;
}