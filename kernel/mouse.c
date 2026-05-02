#include "mouse.h"
#include "io.h"
#include "screen.h"

#define MOUSE_DATA_PORT 0x60
#define MOUSE_STATUS_PORT 0x64

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    inb(0x60);
}

void mouse_handler(void) {
    unsigned char status = inb(MOUSE_STATUS_PORT);
    if (!(status & 0x20)) return;

    unsigned char mouse_data = inb(MOUSE_DATA_PORT);
    static int x = 40, y = 12;
    static unsigned char buttons = 0;

    if (mouse_data & 0x01) buttons |= 1;
    else buttons &= ~1;
    if (mouse_data & 0x02) buttons |= 2;
    else buttons &= ~2;
    if (mouse_data & 0x04) buttons |= 4;
    else buttons &= ~4;

    int dx = (mouse_data & 0x10) ? (mouse_data | 0xFFFFFF00) : (mouse_data & 0x0F);
    int dy = (inb(MOUSE_DATA_PORT) & 0x10) ? (inb(MOUSE_DATA_PORT) | 0xFFFFFF00) : (inb(MOUSE_DATA_PORT) & 0x0F);
    dy = -dy;

    x += dx;
    y += dy;

    if (x < 0) x = 0;
    if (x >= 80) x = 79;
    if (y < 0) y = 0;
    if (y >= 25) y = 24;

    unsigned short *video = (unsigned short*)0xB8000;
    video[y * 80 + x] = 0x0F << 8 | 'M';
}