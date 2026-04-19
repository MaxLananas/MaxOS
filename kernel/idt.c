#include "idt.h"
#include "io.h"

struct idt_entry idt[IDT_ENTRIES];
struct idt_ptr idt_p;

void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags) {
    idt[num].base_low = (base & 0xFFFF);
    idt[num].base_high = (base >> 16) & 0xFFFF;
    idt[num].sel = sel;
    idt[num].always0 = 0;
    idt[num].flags = flags;
}

void idt_init(void) {
    idt_p.limit = (sizeof(struct idt_entry) * IDT_ENTRIES) - 1;
    idt_p.base = (unsigned int)&idt;

    outb(0x20, 0x11);
    outb(0xA0, 0x11);
    outb(0x21, 0x20);
    outb(0xA1, 0x28);
    outb(0x21, 0x04);
    outb(0xA1, 0x02);
    outb(0x21, 0x01);
    outb(0xA1, 0x01);
    outb(0x21, 0x00);
    outb(0xA1, 0x00);

    __asm__ volatile("lidt (%0)" : : "r"(&idt_p));
}

void register_interrupt_handler(unsigned char n, void (*handler)(unsigned int)) {
    idt_set_gate(n, (unsigned int)handler, 0x08, 0x8E);
}