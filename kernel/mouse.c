#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

void mouse_wait(unsigned char type) {
    unsigned int timeout = 100000;
    if (type == 0) {
        while (timeout--) {
            if ((inb(0x64) & 1) == 1) {
                return;
            }
        }
    } else {
        while (timeout--) {
            if ((inb(0x64) & 2) == 0) {
                return;
            }
        }
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
    irq_install_handler(12, mouse_handler);
}

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    if (status & 0x20) {
        unsigned char mouse_data = inb(0x60);
        static unsigned char cycle = 0;
        static unsigned char mouse_bytes[3];
        static int mouse_x = 40;
        static int mouse_y = 12;

        switch (cycle) {
            case 0:
                mouse_bytes[0] = mouse_data;
                if (!(mouse_bytes[0] & 0x08)) return;
                cycle++;
                break;
            case 1:
                mouse_bytes[1] = mouse_data;
                cycle++;
                break;
            case 2:
                mouse_bytes[2] = mouse_data;
                int dx = mouse_bytes[1];
                int dy = mouse_bytes[2];
                if (mouse_bytes[0] & 0x10) dx -= 256;
                if (mouse_bytes[0] & 0x20) dy -= 256;
                mouse_x += dx;
                mouse_y -= dy;

                if (mouse_x < 0) mouse_x = 0;
                if (mouse_x > 79) mouse_x = 79;
                if (mouse_y < 0) mouse_y = 0;
                if (mouse_y > 24) mouse_y = 24;

                screen_putchar('M', 0x0F);
                cycle = 0;
                break;
        }
    }
}