#ifndef IRQ_HANDLER_H
#define IRQ_HANDLER_H

void irq_set_mask(unsigned char irq, unsigned char mask);
void irq_handler(unsigned int num);

#endif