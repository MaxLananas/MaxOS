#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);
    irq_install_handler(12, mouse_handler);
}

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    while ((status & 0x01) == 0) {
        status = inb(0x64);
    }
    unsigned char mouse_data = inb(0x60);
}