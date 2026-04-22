#include "irq.h"
#include "io.h"
#include "idt.h"
#include "isr.h"

void *irq_routines[16] = {
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0
};

void irq_install_handler(unsigned char irq, void (*handler)(registers_t)) {
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
    idt_set_gate(32, (unsigned int)isr32, 0x08, 0x8E);
    idt_set_gate(33, (unsigned int)isr33, 0x08, 0x8E);
    idt_set_gate(34, (unsigned int)isr34, 0x08, 0x8E);
    idt_set_gate(35, (unsigned int)isr35, 0x08, 0x8E);
    idt_set_gate(36, (unsigned int)isr36, 0x08, 0x8E);
    idt_set_gate(37, (unsigned int)isr37, 0x08, 0x8E);
    idt_set_gate(38, (unsigned int)isr38, 0x08, 0x8E);
    idt_set_gate(39, (unsigned int)isr39, 0x08, 0x8E);
    idt_set_gate(40, (unsigned int)isr40, 0x08, 0x8E);
    idt_set_gate(41, (unsigned int)isr41, 0x08, 0x8E);
    idt_set_gate(42, (unsigned int)isr42, 0x08, 0x8E);
    idt_set_gate(43, (unsigned int)isr43, 0x08, 0x8E);
    idt_set_gate(44, (unsigned int)isr44, 0x08, 0x8E);
    idt_set_gate(45, (unsigned int)isr45, 0x08, 0x8E);
    idt_set_gate(46, (unsigned int)isr46, 0x08, 0x8E);
    idt_set_gate(47, (unsigned int)isr47, 0x08, 0x8E);
}

void irq_handler(unsigned int num) {
    void (*handler)(registers_t);
    handler = irq_routines[num - 32];
    if (handler) {
        handler(0);
    }
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}