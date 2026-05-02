#ifndef IRQ_H
#define IRQ_H

void irq_init(void);
void irq_set_handler(unsigned int irq, void (*handler)(void));

#endif