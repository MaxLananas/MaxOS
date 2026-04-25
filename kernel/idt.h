#ifndef IDT_H
#define IDT_H

struct IDTEntry {
    unsigned short base_lo;
    unsigned short sel;
    unsigned char always0;
    unsigned char flags;
    unsigned short base_hi;
} __attribute__((packed));

struct IDTPtr {
    unsigned short limit;
    unsigned int base;
} __attribute__((packed));

void idt_init(void);
void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags);
void idt_load(void);

#endif