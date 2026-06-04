#include "mouse.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    irq_set_gate(12, (unsigned int)irq12, 0x08, 0x8E);
}

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    while (status & 0x01) {
        unsigned char mouse_data = inb(0x60);
        screen_putchar(mouse_data + '0', 0x0F);
        status = inb(0x64);
    }
    outb(0x20, 0x20);
}