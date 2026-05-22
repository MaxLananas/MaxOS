#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "idt.h"

#define MOUSE_DATA 0x60
#define MOUSE_CMD 0x64

static int mouse_x = 40;
static int mouse_y = 12;

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
    idt_set_gate(44, (unsigned int)isr44, 0x08, 0x8E);

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

    outb(0x21, inb(0x21) & ~(1 << 2));
}

void mouse_handler(void) {
    static unsigned char cycle = 0;
    static unsigned char mouse_bytes[3];

    mouse_bytes[cycle++] = inb(0x60);

    if (cycle == 3) {
        cycle = 0;

        int x = mouse_bytes[1];
        int y = mouse_bytes[2];

        if (mouse_bytes[0] & 0x10) x |= 0xFFFFFF00;
        if (mouse_bytes[0] & 0x20) y |= 0xFFFFFF00;
        if (mouse_bytes[0] & 0x40) x = 0;
        if (mouse_bytes[0] & 0x80) y = 0;

        mouse_x += x;
        mouse_y -= y;

        if (mouse_x < 0) mouse_x = 0;
        if (mouse_x > 79) mouse_x = 79;
        if (mouse_y < 0) mouse_y = 0;
        if (mouse_y > 24) mouse_y = 24;

        screen_putchar('M', 0x0F);
    }

    outb(0x20, 0x20);
}