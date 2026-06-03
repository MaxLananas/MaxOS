#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

#define MOUSE_DATA_PORT 0x60
#define MOUSE_STATUS_PORT 0x64

void mouse_init(void)
{
    screen_writeln("Mouse initialized", 0x0A);

    // Enable mouse
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);

    // Set default settings
    outb(0x64, 0xD4);
    outb(0x60, 0xF6);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
}

void mouse_handler(void)
{
    unsigned char status = inb(MOUSE_STATUS_PORT);
    if (status & 0x01) {
        unsigned char mouse_data = inb(MOUSE_DATA_PORT);
        // Process mouse data
    }
}