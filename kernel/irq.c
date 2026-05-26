#include "irq.h"
#include "io.h"
#include "idt.h"
#include "fault_handler.h"

void *irq_routines[16] = {0};

void irq_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags) {
    idt_set_gate(num + 32, base, sel, flags);
}

void irq_install_handler(unsigned char irq, void (*handler)(void)) {
    irq_routines[irq] = handler;
}

void irq_uninstall_handler(unsigned char irq) {
    irq_routines[irq] = 0;
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
        irq_set_gate(i, (unsigned int)irq_stub_table[i], 0x08, 0x8E);
    }
}

void irq_handler(unsigned int num) {
    void (*handler)(void);
    handler = irq_routines[num - 32];
    if (handler != 0) {
        handler();
    }
    pic_send_eoi(num);
}