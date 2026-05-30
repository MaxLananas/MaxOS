#include "irq.h"
#include "idt.h"
#include "io.h"
#include "isr.h"

extern void irq0(void);
extern void irq1(void);
extern void irq2(void);
extern void irq3(void);
extern void irq4(void);
extern void irq5(void);
extern void irq6(void);
extern void irq7(void);
extern void irq8(void);
extern void irq9(void);
extern void irq10(void);
extern void irq11(void);
extern void irq12(void);
extern void irq13(void);
extern void irq14(void);
extern void irq15(void);

void *irq_routines[16] = {
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0
};

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
}

void irq_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags) {
    idt_set_gate(num + 32, base, sel, flags);
}

void irq_install_handler(unsigned char irq, void (*handler)(void)) {
    irq_routines[irq] = handler;
}

void irq_uninstall_handler(unsigned char irq) {
    irq_routines[irq] = 0;
}

void irq_handler(unsigned int num) {
    void (*handler)(void);

    handler = irq_routines[num - 32];
    if (handler) {
        handler();
    }

    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}