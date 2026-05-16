#ifndef IRQ_H
#define IRQ_H

void irq_handler(unsigned int num);
void irq_set_handler(int irq, void (*handler)(void));
void irq_remap(void);

#endif