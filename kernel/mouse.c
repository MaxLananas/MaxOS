#include "mouse.h"
#include "io.h"
#include "screen.h"

#define MOUSE_DATA_PORT 0x60
#define MOUSE_COMMAND_PORT 0x64

static int mouse_x = 40;
static int mouse_y = 12;
static unsigned char mouse_cycle = 0;
static unsigned char mouse_byte[3];

void mouse_wait(unsigned char type) {
    unsigned int timeout = 100000;
    if (type == 0) {
        while (timeout--) {
            if ((inb(MOUSE_COMMAND_PORT) & 1) == 1) {
                return;
            }
        }
    } else {
        while (timeout--) {
            if ((inb(MOUSE_COMMAND_PORT) & 2) == 0) {
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

unsigned char mouse_read(void) {
    mouse_wait(0);
    return inb(MOUSE_DATA_PORT);
}

void mouse_init(void) {
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
}

void mouse_handler(void) {
    unsigned char data = inb(MOUSE_DATA_PORT);
    mouse_byte[mouse_cycle] = data;

    if (mouse_cycle == 0 && !(data & 0x08)) {
        return;
    }

    mouse_cycle++;

    if (mouse_cycle == 3) {
        mouse_cycle = 0;

        int dx = mouse_byte[1];
        int dy = mouse_byte[2];

        if (mouse_byte[0] & 0x10) dx |= 0xFFFFFF00;
        if (mouse_byte[0] & 0x20) dy |= 0xFFFFFF00;

        mouse_x += dx;
        mouse_y -= dy;

        if (mouse_x < 0) mouse_x = 0;
        if (mouse_x >= 80) mouse_x = 79;
        if (mouse_y < 0) mouse_y = 0;
        if (mouse_y >= 25) mouse_y = 24;

        screen_putchar('*', 0x0F);
    }
}