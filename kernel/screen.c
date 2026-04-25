#include "screen.h"
#include "io.h"

#define VGA_WIDTH 80
#define VGA_HEIGHT 25
#define VGA_MEMORY 0xB8000

static unsigned char color = 0x0F;
static unsigned short *video_memory = (unsigned short*)VGA_MEMORY;
static unsigned int row = 0;
static unsigned int col = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    for (unsigned int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    row = 0;
    col = 0;
}

void screen_putchar(char c, unsigned char new_color) {
    if (new_color != color) {
        color = new_color;
    }

    if (c == '\n') {
        row++;
        col = 0;
    } else {
        video_memory[row * VGA_WIDTH + col] = (color << 8) | c;
        col++;
        if (col >= VGA_WIDTH) {
            row++;
            col = 0;
        }
    }

    if (row >= VGA_HEIGHT) {
        screen_scroll();
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
    for (unsigned int i = 0; i < VGA_WIDTH * (VGA_HEIGHT - 1); i++) {
        video_memory[i] = video_memory[i + VGA_WIDTH];
    }

    for (unsigned int i = VGA_WIDTH * (VGA_HEIGHT - 1); i < VGA_WIDTH * VGA_HEIGHT; i++) {
        video_memory[i] = (color << 8) | ' ';
    }

    row = VGA_HEIGHT - 1;
}