#include "irq.h"
#include "idt.h"
#include "io.h"
#include "isr.h"

void (*irq_handlers[16])(void);

void irq_set_handler(unsigned char irq, void (*handler)(unsigned int)) {
    irq_handlers[irq] = handler;
}

void irq_install_handler(unsigned char irq, void (*handler)(void)) {
    irq_handlers[irq] = handler;
}

void irq_uninstall_handler(unsigned char irq) {
    irq_handlers[irq] = 0;
}

void irq_remap(void) {
    outb(0x20, 0x11);
    outb(0xA0, 0x11);
    outb(0x21, 0x20);
    outb(0xA1, 0x28);
    outb(0x21, 0x04);
    outb(0xA1, 0x02);
    outb(0x21, 0x01);
    outb(0xA1, 0x01);
    outb(0x21, 0x0);
    outb(0xA1, 0x0);
}

void irq_init(void) {
    irq_remap();
    for (unsigned int i = 0; i < 16; i++) {
        idt_set_gate(32 + i, (unsigned int)isr32 + i * 8, 0x08, 0x8E);
    }
}

void irq_handler(unsigned int num) {
    void (*handler)(void);
    handler = irq_handlers[num - 32];
    if (handler) {
        handler();
    }
    pic_send_eoi(num - 32);
}