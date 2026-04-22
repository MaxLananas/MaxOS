#include "drivers/screen.h"

#define VGA_WIDTH  80
#define VGA_HEIGHT 25
#define VGA_MEM    ((unsigned short *)0xB8000)

static int cursor_row = 0;
static int cursor_col = 0;
static unsigned char current_color = 0x07;

static void update_hw_cursor(void) {
    unsigned short pos = cursor_row * VGA_WIDTH + cursor_col;
    __asm__ volatile(
        "outb %0, %1" :: "a"((unsigned char)0x0F), "Nd"((unsigned short)0x3D4)
    );
    __asm__ volatile(
        "outb %0, %1" :: "a"((unsigned char)(pos & 0xFF)), "Nd"((unsigned short)0x3D5)
    );
    __asm__ volatile(
        "outb %0, %1" :: "a"((unsigned char)0x0E), "Nd"((unsigned short)0x3D4)
    );
    __asm__ volatile(
        "outb %0, %1" :: "a"((unsigned char)((pos >> 8) & 0xFF)), "Nd"((unsigned short)0x3D5)
    );
}

void screen_scroll(void) {
    int i;
    unsigned short blank = (unsigned short)(' ' | (current_color << 8));
    for (i = 0; i < (VGA_HEIGHT - 1) * VGA_WIDTH; i++) {
        VGA_MEM[i] = VGA_MEM[i + VGA_WIDTH];
    }
    for (i = (VGA_HEIGHT - 1) * VGA_WIDTH; i < VGA_HEIGHT * VGA_WIDTH; i++) {
        VGA_MEM[i] = blank;
    }
    cursor_row = VGA_HEIGHT - 1;
}

void screen_init(void) {
    screen_clear();
}

void screen_clear(void) {
    int i;
    unsigned short blank = (unsigned short)(' ' | (current_color << 8));
    for (i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        VGA_MEM[i] = blank;
    }
    cursor_row = 0;
    cursor_col = 0;
    update_hw_cursor();
}

void screen_putchar(char c, unsigned char color) {
    if (c == '\n') {
        cursor_col = 0;
        cursor_row++;
    } else if (c == '\r') {
        cursor_col = 0;
    } else if (c == '\b') {
        if (cursor_col > 0) {
            cursor_col--;
            VGA_MEM[cursor_row * VGA_WIDTH + cursor_col] = ' ' | (color << 8);
        }
    } else if (c == '\t') {
        cursor_col = (cursor_col + 8) & ~7;
    } else {
        VGA_MEM[cursor_row * VGA_WIDTH + cursor_col] = (unsigned short)(c | (color << 8));
        cursor_col++;
    }
    if (cursor_col >= VGA_WIDTH) {
        cursor_col = 0;
        cursor_row++;
    }
    if (cursor_row >= VGA_HEIGHT) {
        screen_scroll();
    }
    update_hw_cursor();
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
    current_color = color;
}

int screen_get_row(void) {
    return cursor_row;
}

void screen_set_cursor(int row, int col) {
    cursor_row = row;
    cursor_col = col;
    update_hw_cursor();
}
