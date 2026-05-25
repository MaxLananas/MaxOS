#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "isr.h"

#define MOUSE_DATA_PORT 0x60
#define MOUSE_COMMAND_PORT 0x64

static int mouse_x = 40;
static int mouse_y = 12;

void mouse_init(void) {
    outb(MOUSE_COMMAND_PORT, 0xA8);
    outb(MOUSE_COMMAND_PORT, 0x20);
    unsigned char status = inb(MOUSE_DATA_PORT) | 2;
    outb(MOUSE_COMMAND_PORT, 0x60);
    outb(MOUSE_DATA_PORT, status);
    outb(MOUSE_COMMAND_PORT, 0xD4);
    outb(MOUSE_DATA_PORT, 0xF4);
    screen_writeln("Mouse initialized", 0x0B);
}

void mouse_handler(void) {
    unsigned char status = inb(MOUSE_COMMAND_PORT);
    if (status & 0x01) {
        unsigned char mouse_data = inb(MOUSE_DATA_PORT);
        if (mouse_data == 0xFA) {
            return;
        }
        // Simple mouse movement handling
        if (mouse_data & 0x01) {
            mouse_x += (mouse_data & 0x10) ? -1 : 1;
        }
        if (mouse_data & 0x02) {
            mouse_y += (mouse_data & 0x20) ? -1 : 1;
        }
    }
}