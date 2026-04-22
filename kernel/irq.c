#include "kernel/idt.h"
#include "kernel/io.h"
#include "kernel/irq.h"

extern void irq0(void);
extern void irq1(void);
extern void irq2(void);
extern void irq3(void);
extern void irq4(void);
extern void irq5(void);
extern void irq6(void);
     
void irq_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags) {
    idt_set_gate(num + 32, base, sel, flags);
}

void irq_init(void) {
    irq_set_gate(0, (unsigned int)irq0, 0x08, 0x8E);
    irq_set_gate(1, (unsigned int)irq1, 0x08, 0x8E);
    irq_set_gate(2, (unsigned int)irq2, 0x08, 0x8E);
    irq_set_gate(3, (unsigned int)irq3, 0x08, 0x8E);
    irq_set_gate(4, (unsigned int)irq4, 0x08, 0x8E);
    irq_set_gate(5, (unsigned int)irq5, 0x08, 0x8E);
    irq_set_gate(6, (unsigned int)irq6, 0x08, 0x8E);
    irq_set_gate(7, (unsigned int)irq7, 0x08, 0x8E);
    irq_set_gate(8, (unsigned int)irq8, 0x08, 0x8E);
    irq_set_gate(9, (unsigned int)irq9, 0x08, 0x8E);
    irq_set_gate(10, (unsigned int)irq10, 0x08, 0x8E);
    irq_set_gate(11, (unsigned int)irq11, 0x08, 0x8E);
    irq_set_gate(12, (unsigned int)irq12, 0x08, 0x8E);
    irq_set_gate(13, (unsigned int)irq13, 0x08, 0x8E);
    irq_set_gate(14, (unsigned int)irq14, 0x08, 0x8E);
    irq_set_gate(15, (unsigned int)irq15, 0x08, 0x8E);

    outb(0x20, 0x11);
    outb(0xA0, 0x11);
    outb(0x21, 0x20);
    outb(0xA1, 0x28);
    outb(0x21, 0x04);
    outb(0xA1, 0x02);
    outb(0x21, 0x01);
    outb(0xA1, 0x01);
    outb(0x21, 0x00);
    outb(0xA1, 0x00);
}