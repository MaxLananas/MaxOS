#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

#define MOUSE_DATA 0x60
#define MOUSE_CMD 0x64

static int mouse_x = 0;
static int mouse_y = 0;

void mouse_init(void) {
    outb(MOUSE_CMD, 0xA8);
    outb(MOUSE_CMD, 0x20);
    unsigned char status = inb(MOUSE_DATA) | 2;
    outb(MOUSE_CMD, 0x60);
    outb(MOUSE_DATA, status);
    outb(MOUSE_CMD, 0xD4);
    outb(MOUSE_DATA, 0xF4);
    inb(MOUSE_DATA);
    irq_set_handler(12, mouse_handler);
}

void mouse_handler(void) {
    static unsigned char cycle = 0;
    static unsigned char mouse_bytes[3];

    unsigned char data = inb(MOUSE_DATA);

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
            mouse_x += mouse_bytes[1];
            mouse_y -= mouse_bytes[2];
            if (mouse_x < 0) mouse_x = 0;
            if (mouse_y < 0) mouse_y = 0;
            cycle = 0;
            break;
    }

    outb(0x20, 0x20);
}