#include "irq.h"
#include "io.h"
#include "idt.h"
#include "timer.h"
#include "keyboard.h"
#include "mouse.h"

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

void irq_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags) {
    idt_set_gate(num + 32, base, sel, flags);
}

void irq_init(void) {
    for (unsigned int i = 0; i < 16; i++) {
        irq_set_gate(i, (unsigned int)irq0 + i * 4, 0x08, 0x8E);
    }

    outb(0x21, 0xFC);
    outb(0xA1, 0xFF);
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