#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

#define MOUSE_DATA_PORT 0x60
#define MOUSE_COMMAND_PORT 0x64

void mouse_wait(unsigned char type) {
    unsigned int timeout = 100000;
    if (type == 0) {
        while (--timeout && (inb(MOUSE_COMMAND_PORT) & 0x02));
    } else {
        while (--timeout && !(inb(MOUSE_COMMAND_PORT) & 0x01));
    }
}

void mouse_write(unsigned char data) {
    mouse_wait(0);
    outb(MOUSE_COMMAND_PORT, 0xD4);
    mouse_wait(0);
    outb(MOUSE_DATA_PORT, data);
}

unsigned char mouse_read(void) {
    mouse_wait(1);
    return inb(MOUSE_DATA_PORT);
}

void mouse_init(void) {
    mouse_wait(0);
    outb(MOUSE_COMMAND_PORT, 0xA8);
    mouse_wait(0);
    outb(MOUSE_COMMAND_PORT, 0x20);
    mouse_wait(1);
    unsigned char status = inb(MOUSE_DATA_PORT) | 0x02;
    mouse_wait(0);
    outb(MOUSE_COMMAND_PORT, 0x60);
    mouse_wait(0);
    outb(MOUSE_DATA_PORT, status);
    mouse_write(0xF6);
    mouse_read();
    mouse_write(0xF4);
    mouse_read();
    irq_install_handler(12, mouse_handler);
}

void mouse_handler(void) {
    unsigned char status = inb(MOUSE_COMMAND_PORT);
    if (status & 0x01) {
        unsigned char mouse_data = inb(MOUSE_DATA_PORT);
        static unsigned char cycle = 0;
        static unsigned char mouse_bytes[3];
        mouse_bytes[cycle++] = mouse_data;
        if (cycle == 3) {
            cycle = 0;
            int x = mouse_bytes[1];
            int y = mouse_bytes[2];
            if (mouse_bytes[0] & 0x10) x |= 0xFFFFFF00;
            if (mouse_bytes[0] & 0x20) y |= 0xFFFFFF00;
            y = -y;
            screen_putchar('M', 0x0F);
        }
    }
}