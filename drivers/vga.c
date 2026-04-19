#include "vga.h"
#include "../kernel/io.h"

#define VGA_ADDRESS 0xB8000
#define VGA_WIDTH 80
#define VGA_HEIGHT 25

static unsigned short* vga_buffer = (unsigned short*)VGA_ADDRESS;

void vga_init(void) {
    for (unsigned int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga_buffer[i] = (C_BLACK << 12) | (C_BLACK << 8) | ' ';
    }
}

void vga_putchar(char c, unsigned char fg, unsigned char bg) {
    static unsigned int x = 0;
    static unsigned int y = 0;

    if (c == '\n') {
        x = 0;
        y++;
    } else if (c == '\b') {
        if (x > 0) {
            x--;
            vga_buffer[y * VGA_WIDTH + x] = (bg << 12) | (fg << 8) | ' ';
        }
    } else {
        vga_buffer[y * VGA_WIDTH + x] = (bg << 12) | (fg << 8) | c;
        x++;
        if (x >= VGA_WIDTH) {
            x = 0;
            y++;
        }
    }

    if (y >= VGA_HEIGHT) {
        for (unsigned int i = 0; i < VGA_WIDTH * (VGA_HEIGHT - 1); i++) {
            vga_buffer[i] = vga_buffer[i + VGA_WIDTH];
        }
        for (unsigned int i = VGA_WIDTH * (VGA_HEIGHT - 1); i < VGA_WIDTH * VGA_HEIGHT; i++) {
            vga_buffer[i] = (C_BLACK << 12) | (C_BLACK << 8) | ' ';
        }
        y = VGA_HEIGHT - 1;
    }
}

void vga_clear(void) {
    for (unsigned int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga_buffer[i] = (C_BLACK << 12) | (C_BLACK << 8) | ' ';
    }
}