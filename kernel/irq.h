#ifndef IRQ_H
#define IRQ_H

typedef void (*irq_t)(void);

extern irq_t irq_routines[16];

void irq_handler(unsigned int num);

#endif