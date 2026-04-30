#include "mouse.h"
#include "io.h"
#include "irq_handler.h"

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    irq_set_mask(12, 0);
}

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    if (!(status & 0x20)) return;

    unsigned char data = inb(0x60);
}