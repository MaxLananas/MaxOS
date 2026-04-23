#include "mouse.h"
#include "../kernel/io.h"
#include "../kernel/idt.h"
#include "../kernel/screen.h"

#define MOUSE_DATA_PORT 0x60
#define MOUSE_COMMAND_PORT 0x64

static int mouse_x = 0;
static int mouse_y = 0;
static unsigned char mouse_cycle = 0;
static unsigned char mouse_byte[3];

void mouse_wait(unsigned char type) {
    unsigned int timeout = 100000;
    if (type == 0) {
        while (timeout--) {
            if ((inb(MOUSE_COMMAND_PORT) & 0x01) == 1) {
                return;
            }
        }
    } else {
        while (timeout--) {
            if ((inb(MOUSE_COMMAND_PORT) & 0x02) == 0) {
                return;
            }
        }
    }
}

void mouse_write(unsigned char data) {
    mouse_wait(1);
    outb(MOUSE_COMMAND_PORT, 0xD4);
    mouse_wait(1);
    outb(MOUSE_DATA_PORT, data);
}

unsigned char mouse_read() {
    mouse_wait(0);
    return inb(MOUSE_DATA_PORT);
}

void mouse_init() {
    mouse_wait(1);
    outb(MOUSE_COMMAND_PORT, 0xA8);
    mouse_wait(1);
    outb(MOUSE_COMMAND_PORT, 0x20);
    mouse_wait(0);
    unsigned char status = inb(MOUSE_DATA_PORT) | 2;
    mouse_wait(1);
    outb(MOUSE_COMMAND_PORT, 0x60);
    mouse_wait(1);
    outb(MOUSE_DATA_PORT, status);

    mouse_write(0xF6);
    mouse_read();

    mouse_write(0xF4);
    mouse_read();

    idt_set_gate(44, (unsigned int)isr44, 0x08, 0x8E);
    outb(0xA1, inb(0xA1) & 0xEF);
}

void mouse_handler() {
    unsigned char status = inb(MOUSE_COMMAND_PORT);
    if (status & 0x01) {
        unsigned char data = inb(MOUSE_DATA_PORT);
        mouse_byte[mouse_cycle] = data;

        if (mouse_cycle == 2) {
            mouse_x += mouse_byte[1];
            mouse_y -= mouse_byte[2];

            if (mouse_x < 0) mouse_x = 0;
            if (mouse_y < 0) mouse_y = 0;

            screen_write("Mouse moved to X: Y: ", 0x0F);
        }
        mouse_cycle = (mouse_cycle + 1) % 3;
    }
}