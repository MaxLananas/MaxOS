#ifndef ISR_H
#define ISR_H

void isr_handler(unsigned int num, unsigned int err);
void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags);

#endif