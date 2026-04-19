#ifndef IDT_H
#define IDT_H

#define IDT_ENTRIES 256

void idt_init();
void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags);

#endif