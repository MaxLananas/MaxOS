#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

#define MOUSE_DATA_PORT 0x60
#define MOUSE_STATUS_PORT 0x64

static int mouse_x = 40;
static int mouse_y = 12;
static unsigned char mouse_cycle = 0;
static unsigned char mouse_byte[3];

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    outb(0x64, 0x20);
    inb(0x60);
    irq_set_gate(12, (unsigned int)irq12, 0x08, 0x8E);
}

void mouse_handler(void) {
    unsigned char data = inb(MOUSE_DATA_PORT);

    switch (mouse_cycle) {
        case 0:
            mouse_byte[0] = data;
            mouse_cycle++;
            break;
        case 1:
            mouse_byte[1] = data;
            mouse_cycle++;
            break;
        case 2:
            mouse_byte[2] = data;
            mouse_cycle = 0;

            if (mouse_byte[0] & 0x80 || mouse_byte[0] & 0x40) {
                break;
            }

            int dx = mouse_byte[1];
            int dy = mouse_byte[2];

            if (mouse_byte[0] & 0x10) dx |= 0xFFFFFF00;
            if (mouse_byte[0] & 0x20) dy |= 0xFFFFFF00;
            dy = -dy;

            mouse_x += dx;
            mouse_y += dy;

            if (mouse_x < 0) mouse_x = 0;
            if (mouse_y < 0) mouse_y = 0;
            if (mouse_x >= 80) mouse_x = 79;
            if (mouse_y >= 25) mouse_y = 24;

            break;
    }

    outb(0x20, 0x20);
}