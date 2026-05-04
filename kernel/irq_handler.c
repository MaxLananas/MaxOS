#include "irq.h"
#include "idt.h"
#include "io.h"
#include "screen.h"

extern void *irq_routines[];

void irq_handler(unsigned int num) {
    void (*handler)(struct regs *r);
    handler = irq_routines[num - 32];
    if (handler != 0) {
        handler((struct regs*)(&num - 2));
    }
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}