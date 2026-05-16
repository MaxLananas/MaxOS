#include "screen.h"
#include "io.h"

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY 0xB8000

static unsigned char color = 0x0F;
static unsigned short *video_memory = (unsigned short *)VGA_MEMORY;
static unsigned int row = 0;
static unsigned int column = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (int i = 0; i < VGA_HEIGHT; i++) {
        for (int j = 0; j < VGA_WIDTH; j++) {
            video_memory[i * VGA_WIDTH + j] = (color << 8) | ' ';
        }
    }
    row = 0;
    column = 0;
}

void screen_putchar(char c, unsigned char new_color) {
    if (new_color != color) {
        color = new_color;
    }

    if (c == '\n') {
        row++;
        column = 0;
        if (row >= VGA_HEIGHT) {
            screen_scroll();
            row = VGA_HEIGHT - 1;
        }
        return;
    }

    video_memory[row * VGA_WIDTH + column] = (color << 8) | c;
    column++;

    if (column >= VGA_WIDTH) {
        column = 0;
        row++;
        if (row >= VGA_HEIGHT) {
            screen_scroll();
            row = VGA_HEIGHT - 1;
        }
    }
}

void screen_write(const char *str, unsigned char new_color) {
    while (*str) {
        screen_putchar(*str++, new_color);
    }
}

void screen_writeln(const char *str, unsigned char new_color) {
    screen_write(str, new_color);
    screen_putchar('\n', new_color);
}

void screen_set_color(unsigned char new_color) {
    color = new_color;
}

int screen_get_row(void) {
    return row;
}

void screen_scroll(void) {
    for (int i = 1; i < VGA_HEIGHT; i++) {
        for (int j = 0; j < VGA_WIDTH; j++) {
            video_memory[(i - 1) * VGA_WIDTH + j] = video_memory[i * VGA_WIDTH + j];
        }
    }

    for (int j = 0; j < VGA_WIDTH; j++) {
        video_memory[(VGA_HEIGHT - 1) * VGA_WIDTH + j] = (color << 8) | ' ';
    }
}