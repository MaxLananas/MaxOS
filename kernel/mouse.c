#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

#define MOUSE_DATA_PORT 0x60
#define MOUSE_CMD_PORT 0x64

static int mouse_x = 0;
static int mouse_y = 0;

void mouse_init(void) {
    outb(MOUSE_CMD_PORT, 0xA8);
    outb(MOUSE_CMD_PORT, 0x20);
    unsigned char status = inb(MOUSE_DATA_PORT) | 2;
    outb(MOUSE_CMD_PORT, 0x60);
    outb(MOUSE_DATA_PORT, status);
    outb(MOUSE_CMD_PORT, 0xD4);
    outb(MOUSE_DATA_PORT, 0xF4);
    irq_install_handler(12, mouse_handler);
}

void mouse_handler(void) {
    unsigned char status = inb(MOUSE_CMD_PORT);
    if (status & 0x01) {
        unsigned char data = inb(MOUSE_DATA_PORT);
        mouse_x += (data & 0x10) ? (data | 0xFFFFFF00) : data;
        mouse_y -= ((data >> 4) & 0x01) ? ((data >> 4) | 0xFFFFFFF0) : (data >> 4);
    }
    outb(0x20, 0x20);
}