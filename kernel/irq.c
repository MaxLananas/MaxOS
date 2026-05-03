#include "irq.h"
#include "idt.h"
#include "io.h"

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

void *irq_routines[16] = {0};

void irq_install_handler(int irq, void (*handler)(void)) {
    irq_routines[irq] = handler;
    idt_set_gate(32 + irq, (unsigned int)irq0 + irq * 4, 0x08, 0x8E);
}

void irq_uninstall_handler(int irq) {
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