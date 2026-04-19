#ifndef IDT_H
#define IDT_H

void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags);
void idt_load();
void idt_init();

#endif