#include "irq.h"
#include "io.h"
#include "screen.h"
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

void irq_set_gate(unsigned char irq, unsigned int base, unsigned short sel, unsigned char flags) {
    idt_set_gate(irq + 32, base, sel, flags);
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