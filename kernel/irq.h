#ifndef IRQ_H
#define IRQ_H

#include "kernel/timer.h"

void (*interrupt_handlers[256])(struct regs *r);
void register_interrupt_handler(unsigned char n, void (*handler)(struct regs *r));
void irq_handler(unsigned int num);

#endif