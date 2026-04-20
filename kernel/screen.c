#include "screen.h"
#include "io.h"

#define VIDEO_MEMORY 0xB8000
#define MAX_ROWS 25
#define MAX_COLS 80
#define WHITE_ON_BLACK 0x0F

static unsigned short* video_memory = (unsigned short*)VIDEO_MEMORY;
static unsigned int cursor_row = 0;
static unsigned int cursor_col = 0;

void screen_clear() {
    unsigned int i;
    for (i = 0; i < MAX_ROWS * MAX_COLS; i++) {
        video_memory[i] = (WHITE_ON_BLACK << 8) | ' ';
    }
    cursor_row = 0;
    cursor_col = 0;
}

void screen_write(const char* str) {
    unsigned int i = 0;
    while (str[i]) {
        if (cursor_row >= MAX_ROWS) {
            screen_clear();
        }

        if (str[i] == '\n') {
            cursor_col = 0;
            cursor_row++;
        } else {
            video_memory[cursor_row * MAX_COLS + cursor_col] =
                (WHITE_ON_BLACK << 8) | str[i];
            cursor_col++;
            if (cursor_col >= MAX_COLS) {
                cursor_col = 0;
                cursor_row++;
            }
        }
        i++;
    }
}

void screen_write_hex(unsigned int num) {
    char hex_chars[] = "0123456789ABCDEF";
    char buffer[9];
    buffer[8] = '\0';

    for (int i = 7; i >= 0; i--) {
        buffer[i] = hex_chars[num & 0xF];
        num >>= 4;
    }

    screen_write(buffer);
}