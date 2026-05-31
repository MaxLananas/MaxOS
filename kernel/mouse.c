#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "idt.h"

#define MOUSE_DATA_PORT 0x60
#define MOUSE_CMD_PORT 0x64

static int mouse_x = 40;
static int mouse_y = 12;

void mouse_init(void) {
    outb(MOUSE_CMD_PORT, 0xA8);
    outb(MOUSE_CMD_PORT, 0x20);
    unsigned char status = inb(MOUSE_DATA_PORT) | 2;
    outb(MOUSE_CMD_PORT, 0x60);
    outb(MOUSE_DATA_PORT, status);
    outb(MOUSE_CMD_PORT, 0xD4);
    outb(MOUSE_DATA_PORT, 0xF4);
    idt_set_gate(44, (unsigned int)mouse_handler, 0x08, 0x8E);
}

void mouse_handler(void) {
    unsigned char status = inb(MOUSE_CMD_PORT);
    if (!(status & 0x20)) return;

    unsigned char mouse_in = inb(MOUSE_DATA_PORT);
    if (mouse_in & 0x01) {
        static unsigned char cycle = 0;
        static unsigned char mouse_bytes[3];
        mouse_bytes[cycle++] = mouse_in;

        if (cycle == 3) {
            cycle = 0;
            int dx = mouse_bytes[1];
            int dy = mouse_bytes[2];

            if (mouse_bytes[0] & 0x10) dx |= 0xFFFFFF00;
            if (mouse_bytes[0] & 0x20) dy |= 0xFFFFFF00;

            mouse_x += dx;
            mouse_y -= dy;

            if (mouse_x < 0) mouse_x = 0;
            if (mouse_x >= 80) mouse_x = 79;
            if (mouse_y < 0) mouse_y = 0;
            if (mouse_y >= 25) mouse_y = 24;

            screen_putchar('M', 0x0F);
        }
    }
    outb(0x20, 0x20);
}