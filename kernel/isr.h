#ifndef ISR_H
#define ISR_H

void isr_handler(unsigned int num, unsigned int err);
void irq_handler(unsigned int num);
void register_interrupt_handler(unsigned char n, void (*handler)(void));

#endif