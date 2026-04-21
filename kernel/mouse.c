#include "io.h"
#include "mouse.h"
#include "screen.h"
#include "idt.h"

static int mouse_x = 40;
static int mouse_y = 12;
static unsigned char mouse_cycle = 0;
static char mouse_byte[3];
static unsigned char mouse_buttons = 0;

void mouse_wait(unsigned char type) {
    unsigned int timeout = 100000;
    if (type == 0) {
        while (timeout--) {
            if ((inb(0x64) & 1) == 1) return;
        }
    } else {
        while (timeout--) {
            if ((inb(0x64) & 2) == 0) return;
        }
    }
}

void mouse_write(unsigned char data) {
    mouse_wait(1);
    outb(0x64, 0xD4);
    mouse_wait(1);
    outb(0x60, data);
}

unsigned char mouse_read() {
    mouse_wait(0);
    return inb(0x60);
}

void mouse_init(void) {
    unsigned char status;

    mouse_wait(1);
    outb(0x64, 0xA8);

    mouse_wait(1);
    outb(0x64, 0x20);
    mouse_wait(0);
    status = inb(0x60) | 2;
    mouse_wait(1);
    outb(0x64, 0x60);
    mouse_wait(1);
    outb(0x60, status);

    mouse_write(0xF6);
    mouse_read();

    mouse_write(0xF4);
    mouse_read();

    idt_set_gate(44, (unsigned int)mouse_handler, 0x08, 0x8E);
}

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    if (!(status & 0x20)) return;

    switch (mouse_cycle) {
        case 0:
            mouse_byte[0] = mouse_read();
            if (!(mouse_byte[0] & 0x08)) return;
            mouse_cycle++;
            break;
        case 1:
            mouse_byte[1] = mouse_read();
            mouse_cycle++;
            break;
        case 2:
            mouse_byte[2] = mouse_read();
            mouse_buttons = mouse_byte[0] & 0x07;

            if (mouse_byte[0] & 0x10) mouse_x -= mouse_byte[1];
            if (mouse_byte[0] & 0x20) mouse_x += mouse_byte[1];
            if (mouse_byte[0] & 0x40) mouse_y -= mouse_byte[2];
            if (mouse_byte[0] & 0x80) mouse_y += mouse_byte[2];

            if (mouse_x < 0) mouse_x = 0;
            if (mouse_y < 0) mouse_y = 0;
            if (mouse_x > 79) mouse_x = 79;
            if (mouse_y > 24) mouse_y = 24;

            mouse_cycle = 0;
            break;
    }

    outb(0x20, 0x20);
    outb(0xA0, 0x20);
}