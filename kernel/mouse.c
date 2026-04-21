#include "mouse.h"
#include "idt.h"
#include "io.h"
#include "screen.h"

#define MOUSE_DATA_PORT 0x60
#define MOUSE_STATUS_PORT 0x64

void mouse_wait(unsigned char type) {
    unsigned int timeout = 100000;
    if (type == 0) {
        while (timeout--) {
            if ((inb(MOUSE_STATUS_PORT) & 0x01) == 1) {
                return;
            }
        }
    } else {
        while (timeout--) {
            if ((inb(MOUSE_STATUS_PORT) & 0x02) == 0) {
                return;
            }
        }
    }
}

void mouse_write(unsigned char data) {
    mouse_wait(1);
    outb(MOUSE_STATUS_PORT, 0xD4);
    mouse_wait(1);
    outb(MOUSE_DATA_PORT, data);
}

unsigned char mouse_read(void) {
    mouse_wait(0);
    return inb(MOUSE_DATA_PORT);
}

void mouse_init(void) {
    mouse_wait(1);
    outb(MOUSE_STATUS_PORT, 0xA8);
    mouse_wait(1);
    outb(MOUSE_STATUS_PORT, 0x20);
    mouse_wait(0);
    unsigned char status = inb(MOUSE_DATA_PORT) | 2;
    mouse_wait(1);
    outb(MOUSE_STATUS_PORT, 0x60);
    mouse_wait(1);
    outb(MOUSE_DATA_PORT, status);
    mouse_write(0xF6);
    mouse_read();
    mouse_write(0xF4);
    mouse_read();
    idt_set_gate(44, (unsigned int)isr44, 0x08, 0x8E);
}

void mouse_handler(void) {
    static unsigned char cycle = 0;
    static char mouse_bytes[3];
    unsigned char data = inb(MOUSE_DATA_PORT);

    switch (cycle) {
        case 0:
            if ((data & 0x08) == 0) break;
            mouse_bytes[0] = data;
            cycle++;
            break;
        case 1:
            mouse_bytes[1] = data;
            cycle++;
            break;
        case 2:
            mouse_bytes[2] = data;
            screen_putchar('M', 0x07);
            cycle = 0;
            break;
    }
    outb(0x20, 0x20);
}