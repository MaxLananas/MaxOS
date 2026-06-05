#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

#define MOUSE_DATA_PORT 0x60
#define MOUSE_CMD_PORT 0x64

static int mouse_x = 0;
static int mouse_y = 0;
static unsigned char mouse_cycle = 0;
static unsigned char mouse_byte[3];

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

            mouse_x += mouse_byte[1];
            mouse_y -= mouse_byte[2];

            if (mouse_x < 0) mouse_x = 0;
            if (mouse_y < 0) mouse_y = 0;
            break;
    }
}