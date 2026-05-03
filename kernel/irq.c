#include "irq.h"
#include "io.h"
#include "idt.h"

extern void irq0();
extern void irq1();
extern void irq2();
extern void irq3();
extern void irq4();
extern void irq5();
extern void irq6();
extern void irq7();
extern void irq8();
extern void irq9();
extern void irq10();
extern void irq11();
extern void irq12();
extern void irq13();
extern void irq14();
extern void irq15();

void *irq_routines[16] = {
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0
};

void irq_install_handler(int irq, void (*handler)(void)) {
    irq_routines[irq] = handler;
    idt_set_gate(32 + irq, (unsigned int)irq0 + irq * 8, 0x08, 0x8E);
}

void irq_uninstall_handler(int irq) {
    irq_routines[irq] = 0;
}

void irq_handler(struct regs *r) {
    void (*handler)(struct regs *r);
    handler = irq_routines[r->int_no - 32];
    if (handler) {
        handler(r);
    }
    if (r->int_no >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}