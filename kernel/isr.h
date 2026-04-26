#ifndef ISR_H
#define ISR_H

typedef void (*isr_t)(unsigned int err);

void register_interrupt_handler(unsigned char n, isr_t handler);
void isr_handler(unsigned int num, unsigned int err);

#endif