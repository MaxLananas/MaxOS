#ifndef IRQ_H
#define IRQ_H

void irq_init(void);
void irq_set_handler(unsigned char irq, void (*handler)(void));
void irq_handler(unsigned int num);

#endif