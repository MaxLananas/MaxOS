#ifndef IRQ_H
#define IRQ_H

void irq_init(void);
void irq_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags);

#endif