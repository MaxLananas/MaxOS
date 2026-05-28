#ifndef IRQ_H
#define IRQ_H

void irq_set_mask(unsigned char irq_line, unsigned char mask);
void irq_init(void);

#endif