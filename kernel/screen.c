#include "screen.h"
#include "io.h"

#define VIDEO_MEMORY 0xB8000
#define MAX_ROWS 25
#define MAX_COLS 80
#define TAB_SIZE 4

static unsigned char color = 0x0F;
static unsigned int cursor_pos = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    unsigned short *video_memory = (unsigned short *)VIDEO_MEMORY;
    for (unsigned int i = 0; i < MAX_ROWS * MAX_COLS; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    cursor_pos = 0;
}

void screen_putchar(char c, unsigned char color) {
    unsigned short *video_memory = (unsigned short *)VIDEO_MEMORY;
    unsigned int index = cursor_pos;
    unsigned int row = index / MAX_COLS;
    unsigned int col = index % MAX_COLS;

    if (c == '\n') {
        cursor_pos = (row + 1) * MAX_COLS;
    } else if (c == '\t') {
        unsigned int next_tab = ((col / TAB_SIZE) + 1) * TAB_SIZE;
        cursor_pos += next_tab - col;
    } else {
        video_memory[index] = (color << 8) | (unsigned char)c;
        cursor_pos++;
    }

    if (cursor_pos >= MAX_ROWS * MAX_COLS) {
        screen_scroll();
        cursor_pos = (MAX_ROWS - 1) * MAX_COLS;
    }

    unsigned short pos = cursor_pos;
    outb(0x3D4, 0x0F);
    outb(0x3D5, (unsigned char)(pos & 0xFF));
    outb(0x3D4, 0x0E);
    outb(0x3D5, (unsigned char)((pos >> 8) & 0xFF));
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
    return cursor_pos / MAX_COLS;
}

void screen_scroll(void) {
    unsigned short *video_memory = (unsigned short *)VIDEO_MEMORY;
    for (unsigned int i = 0; i < (MAX_ROWS - 1) * MAX_COLS; i++) {
        video_memory[i] = video_memory[i + MAX_COLS];
    }
    for (unsigned int i = (MAX_ROWS - 1) * MAX_COLS; i < MAX_ROWS * MAX_COLS; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
}