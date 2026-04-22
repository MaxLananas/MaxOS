#ifndef ISR_H
#define ISR_H

void register_interrupt_handler(unsigned char n, void (*handler)(unsigned int, unsigned int));
void isr_handler(unsigned int num, unsigned int err);

#endif