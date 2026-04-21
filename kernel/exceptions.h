#ifndef EXCEPTIONS_H
#define EXCEPTIONS_H

void isr_handler(unsigned int num, unsigned int err);
void irq_handler(unsigned int num);

#endif