#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

#define MOUSE_DATA_PORT 0x60
#define MOUSE_STATUS_PORT 0x64

void mouse_wait(unsigned char type)
{
    unsigned int timeout = 100000;
    if (type == 0) {
        while (timeout--) {
            if ((inb(MOUSE_STATUS_PORT) & 1) == 1) {
                return;
            }
        }
    } else {
        while (timeout--) {
            if ((inb(MOUSE_STATUS_PORT) & 2) == 0) {
                return;
            }
        }
    }
}

void mouse_write(unsigned char data)
{
    mouse_wait(1);
    outb(MOUSE_STATUS_PORT, 0xD4);
    mouse_wait(1);
    outb(MOUSE_DATA_PORT, data);
}

unsigned char mouse_read(void)
{
    mouse_wait(0);
    return inb(MOUSE_DATA_PORT);
}

void mouse_handler(void)
{
    unsigned char status = inb(MOUSE_STATUS_PORT);
    if (status & 0x01) {
        unsigned char mouse_data = inb(MOUSE_DATA_PORT);
        static unsigned char cycle = 0;
        static unsigned char mouse_bytes[3];
        mouse_bytes[cycle++] = mouse_data;

        if (cycle == 3) {
            cycle = 0;
            if (mouse_bytes[0] & 0x80 || mouse_bytes[0] & 0x40) {
                return;
            }
        }
    }
}

void mouse_init(void)
{
    mouse_wait(1);
    outb(MOUSE_STATUS_PORT, 0xA8);
    mouse_wait(1);
    outb(MOUSE_STATUS_PORT, 0x20);
    mouse_wait(0);
    unsigned char status = inb(MOUSE_DATA_PORT) | 2;
    mouse_wait(1);
    outb(MOUSE_STATUS_PORT, 0x60);
    mouse_wait(1);
    outb(MOUSE_DATA_PORT, status);
    mouse_write(0xF6);
    mouse_read();
    mouse_write(0xF4);
    mouse_read();
    irq_install_handler(12, mouse_handler);
}