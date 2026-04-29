#include "idt.h"
#include "io.h"

void idt_init(void) {
    unsigned int idt_ptr[2];
    struct IDTEntry *idt = (struct IDTEntry*)0x8000;

    for (int i = 0; i < 256; i++) {
        idt_set_gate(i, 0, 0, 0);
    }

    idt_load();
}

void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags) {
    struct IDTEntry *idt = (struct IDTEntry*)0x8000;
    idt[num].base_lo = base & 0xFFFF;
    idt[num].base_hi = (base >> 16) & 0xFFFF;
    idt[num].sel = sel;
    idt[num].always0 = 0;
    idt[num].flags = flags | 0x60;
}

void idt_load(void) {
    struct IDTPtr idt_ptr;
    idt_ptr.limit = 256 * sizeof(struct IDTEntry) - 1;
    idt_ptr.base = 0x8000;
    __asm__ volatile("lidt %0" : : "m"(idt_ptr));
}