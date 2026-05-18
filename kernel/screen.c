#include "screen.h"
#include "io.h"

#define VIDEO_MEMORY 0xB8000
#define MAX_ROWS 25
#define MAX_COLS 80
#define DEFAULT_COLOR 0x0F

static unsigned char color = DEFAULT_COLOR;
static unsigned short *video_memory = (unsigned short*)VIDEO_MEMORY;
static unsigned int row = 0;
static unsigned int col = 0;

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    unsigned int i;
    for (i = 0; i < MAX_ROWS * MAX_COLS; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    row = 0;
    col = 0;
}

void screen_putchar(char c, unsigned char new_color) {
    if (new_color != 0) color = new_color;

    if (c == '\n') {
        row++;
        col = 0;
        if (row >= MAX_ROWS) {
            screen_scroll();
            row = MAX_ROWS - 1;
        }
        return;
    }

    video_memory[row * MAX_COLS + col] = (color << 8) | c;
    col++;

    if (col >= MAX_COLS) {
        row++;
        col = 0;
        if (row >= MAX_ROWS) {
            screen_scroll();
            row = MAX_ROWS - 1;
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
    screen_putchar('\n', 0);
}

void screen_set_color(unsigned char new_color) {
    color = new_color;
}

int screen_get_row(void) {
    return row;
}

void screen_scroll(void) {
    unsigned int i;
    for (i = 0; i < (MAX_ROWS - 1) * MAX_COLS; i++) {
        video_memory[i] = video_memory[i + MAX_COLS];
    }
    for (i = (MAX_ROWS - 1) * MAX_COLS; i < MAX_ROWS * MAX_COLS; i++) {
        video_memory[i] = (color << 8) | ' ';
    }
    if (row > 0) row--;
}
```=== END FILE ===