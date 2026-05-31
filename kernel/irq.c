#include "irq.h"
#include "io.h"
#include "idt.h"
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

void *irq_routines[16] = {0};

void irq_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags)
{
    idt_set_gate(num + 32, base, sel, flags);
}

void irq_install_handler(int irq, void (*handler)(void))
{
    irq_routines[irq] = handler;
}

void irq_uninstall_handler(int irq)
{
    irq_routines[irq] = 0;
}

void irq_remap(void)
{
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

void irq_init(void)
{
    irq_remap();
    for (int i = 0; i < 16; i++) {
        irq_set_gate(i, (unsigned int)irq0 + i * 4, 0x08, 0x8E);
    }
}