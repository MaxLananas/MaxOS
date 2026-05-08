#include "drivers/mouse.h"
#include "kernel/io.h"
#include "kernel/idt.h"

void mouse_init(void) {
    unsigned char status;

    outb(0x64, 0xA8);
    outb(0x64, 0x20);
    status = inb(0x64) | 2;
    outb(0x64, 0x60);
    outb(0x60, status);

    outb(0x64, 0xD4);
    outb(0x60, 0xF4);

    outb(0x64, 0x20);
    status = inb(0x60);
    outb(0x64, 0x60);
    outb(0x60, status);

    idt_set_gate(44, (unsigned int)mouse_handler, 0x08, 0x8E);
}

void mouse_handler(void) {
    unsigned char status;
    status = inb(0x64);
    if (status & 0x01) {
        unsigned char data = inb(0x60);
    }
}