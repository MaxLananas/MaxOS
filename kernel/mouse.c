#include "screen.h"
#include "io.h"

#define MOUSE_DATA_PORT 0x60
#define MOUSE_STATUS_PORT 0x64

void mouse_init(void) {
    unsigned char status;

    // Enable mouse
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);

    // Set default settings
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);

    screen_writeln("Mouse initialized", 0x0F);
}

void mouse_handler(void) {
    unsigned char mouse_data = inb(MOUSE_DATA_PORT);
    static unsigned int mouse_x = 40;
    static unsigned int mouse_y = 12;

    // Simple mouse movement handling
    if (mouse_data & 0x01) {
        mouse_x += (mouse_data & 0x10) ? -1 : 1;
        mouse_y += (mouse_data & 0x20) ? -1 : 1;
    }

    screen_putchar('M', 0x0F);
}