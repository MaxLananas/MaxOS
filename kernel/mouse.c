#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

void mouse_wait(unsigned char type) {
    unsigned int timeout = 100000;
    if (type == 0) {
        while (--timeout && (inb(0x64) & 1));
    } else {
        while (--timeout && (inb(0x64) & 2));
    }
}

void mouse_write(unsigned char data) {
    mouse_wait(1);
    outb(0x64, 0xD4);
    mouse_wait(1);
    outb(0x60, data);
}

unsigned char mouse_read(void) {
    mouse_wait(0);
    return inb(0x60);
}

void mouse_init(void) {
    mouse_wait(1);
    outb(0x64, 0xA8);
    mouse_wait(1);
    outb(0x64, 0x20);
    mouse_wait(0);
    unsigned char status = inb(0x60) | 2;
    mouse_wait(1);
    outb(0x64, 0x60);
    mouse_wait(1);
    outb(0x60, status);
    mouse_write(0xF6);
    mouse_read();
    mouse_write(0xF4);
    mouse_read();
}

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    if (status & 0x20) {
        unsigned char mouse_data = inb(0x60);
        static int mouse_x = 40;
        static int mouse_y = 12;
        static unsigned char mouse_button = 0;

        if (mouse_data & 0x01) mouse_button |= 1;
        else mouse_button &= ~1;
        if (mouse_data & 0x02) mouse_button |= 2;
        else mouse_button &= ~2;
        if (mouse_data & 0x04) mouse_button |= 4;
        else mouse_button &= ~4;

        int dx = (signed char)((mouse_data & 0x30) ? (mouse_data | 0xFFFFFFC0) : (mouse_data & 0x3F));
        int dy = (signed char)((mouse_data & 0xC0) ? (mouse_data | 0xFFFFFF00) : (mouse_data & 0x3F));

        mouse_x += dx;
        mouse_y -= dy;

        if (mouse_x < 0) mouse_x = 0;
        if (mouse_x >= 80) mouse_x = 79;
        if (mouse_y < 0) mouse_y = 0;
        if (mouse_y >= 25) mouse_y = 24;

        video_memory[mouse_y * 80 + mouse_x] = 0x0F00 | 'M';
    }
}