#include "io.h"
#include "idt.h"
#include "mouse.h"

extern void irq_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags);

void mouse_handler(void) {
    unsigned char status = inb(0x64);
    if (status & 0x01) {
        unsigned char data = inb(0x60);
    }
}

void mouse_init(void) {
    irq_set_gate(44, (unsigned int)mouse_handler, 0x08, 0x8E);
}