#include "mouse.h"
#include "io.h"
#include "idt.h"
#include "irq.h"

#define MOUSE_DATA_PORT 0x60
#define MOUSE_STATUS_PORT 0x64

void mouse_init(void) {
    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    unsigned char status = inb(0x60) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);
    outb(0x64, 0xD4);
    outb(0x60, 0xF4);
    inb(0x60);

    idt_set_gate(44, (unsigned int)mouse_handler, 0x08, 0x8E);
    irq_install_handler(12, mouse_handler);
}

void mouse_handler(void) {
    unsigned char status = inb(MOUSE_STATUS_PORT);
    if (status & 0x01) {
        unsigned char data = inb(MOUSE_DATA_PORT);
    }
    outb(0x20, 0x20);
}