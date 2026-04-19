#include "screen.h"
#include "../kernel/io.h"
#include "pci.h"

#define VGA_ADDRESS 0xB8000
#define VGA_WIDTH 80
#define VGA_HEIGHT 25

static unsigned short* vga_buffer = (unsigned short*)VGA_ADDRESS;
static unsigned int cursor_x = 0;
static unsigned int cursor_y = 0;

void v_init(void) {
    pci_probe_vga();
    for (unsigned int i = 0; i < VGA_WIDTH * VGA_HEIGHT; i++) {
        vga_buffer[i] = (C_BLACK << 12) | (C_BLACK << 8) | ' ';
    }
    cursor_x = 0;
    cursor_y = 0;
}

void v_put(unsigned int x, unsigned int y, char c, unsigned char fg, unsigned char bg) {
    if (x >= VGA_WIDTH || y >= VGA_HEIGHT) {
        return;
    }
    unsigned short attr = (bg << 12) | (fg << 8);
    vga_buffer[y * VGA_WIDTH + x] = attr | c;
}

void v_str(unsigned int x, unsigned int y, const char* s, unsigned char fg, unsigned char bg) {
    while (*s) {
        v_put(x++, y, *s++, fg, bg);
        if (x >= VGA_WIDTH) {
            x = 0;
            y++;
            if (y >= VGA_HEIGHT) {
                y = 0;
            }
        }
    }
}

void v_fill(unsigned int x1, unsigned int y1, unsigned int x2, unsigned int y2, unsigned char fg, unsigned char bg) {
    for (unsigned int y = y1; y <= y2 && y < VGA_HEIGHT; y++) {
        for (unsigned int x = x1; x <= x2 && x < VGA_WIDTH; x++) {
            v_put(x, y, ' ', fg, bg);
        }
    }
}