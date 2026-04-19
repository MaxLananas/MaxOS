#ifndef IDT_H
#define IDT_H

#define IDT_ENTRIES 256

struct idt_entry {
    unsigned short base_low;
    unsigned short sel;
    unsigned char always0;
    unsigned char flags;
    unsigned short base_high;
} __attribute__((packed));

struct idt_ptr {
    unsigned short limit;
    unsigned int base;
} __attribute__((packed));

void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags);
void idt_init(void);
void register_interrupt_handler(unsigned char n, void (*handler)(unsigned int));

#endif