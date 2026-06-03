#include "irq.h"
#include "io.h"
#include "screen.h"

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

void *irq_routines[16] = {0};

void irq_set_mask(unsigned char irq, unsigned char mask)
{
    unsigned short port;
    unsigned char value;

    if (irq < 8)
        port = 0x21;
    else
    {
        port = 0xA1;
        irq -= 8;
    }

    value = inb(port);
    if (mask)
        value |= (1 << irq);
    else
        value &= ~(1 << irq);
    outb(port, value);
}

void irq_init(void)
{
    for (unsigned int i = 0; i < 16; i++)
        irq_set_mask(i, 1);

    irq_set_mask(0, 0);
    irq_set_mask(1, 0);
    irq_set_mask(12, 0);
}

void irq_install_handler(unsigned int irq, void (*handler)(void))
{
    irq_routines[irq] = handler;
}

void irq_uninstall_handler(unsigned int irq)
{
    irq_routines[irq] = 0;
}

void irq_handler(unsigned int num)
{
    void (*handler)(void);

    handler = irq_routines[num - 32];
    if (handler)
        handler();

    if (num >= 40)
        outb(0xA0, 0x20);

    outb(0x20, 0x20);
}