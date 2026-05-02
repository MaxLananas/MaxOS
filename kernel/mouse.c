#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

#define MOUSE_DATA_PORT 0x60
#define MOUSE_COMMAND_PORT 0x64

static int mouse_x = 40;
static int mouse_y = 12;

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
    screen_writeln("Mouse initialized", 0x0A);
}

void mouse_handler(void) {
    static unsigned char cycle = 0;
    static char mouse_bytes[3];
    unsigned char data = inb(MOUSE_DATA_PORT);

    mouse_bytes[cycle++] = data;
    if (cycle == 3) {
        cycle = 0;
        int x = mouse_bytes[1];
        int y = mouse_bytes[2];

        if (mouse_bytes[0] & 0x10) x |= 0xFFFFFF00;
        if (mouse_bytes[0] & 0x20) y |= 0xFFFFFF00;
        if (mouse_bytes[0] & 0x40) x = 0;
        if (mouse_bytes[0] & 0x80) y = 0;

        mouse_x += x;
        mouse_y -= y;

        if (mouse_x < 0) mouse_x = 0;
        if (mouse_y < 0) mouse_y = 0;
        if (mouse_x >= 80) mouse_x = 79;
        if (mouse_y >= 25) mouse_y = 24;

        unsigned short *vga = (unsigned short*)0xB8000;
        vga[mouse_y * 80 + mouse_x] = 0x0F00 | 'M';
    }
}