#include "idt.h"
#include "isr.h"

struct IDTEntry idt_entries[256];
struct IDTPtr idt_ptr;

extern void idt_load(struct IDTPtr *idtp);

void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags) {
    idt_entries[num].base_lo = base & 0xFFFF;
    idt_entries[num].base_hi = (base >> 16) & 0xFFFF;
    idt_entries[num].sel = sel;
    idt_entries[num].always0 = 0;
    idt_entries[num].flags = flags;
}

void idt_init(void) {
    idt_ptr.limit = sizeof(idt_entries) - 1;
    idt_ptr.base = (unsigned int)&idt_entries;

    for (unsigned int i = 0; i < 256; i++) {
        idt_set_gate(i, 0, 0, 0);
    }

    idt_load(&idt_ptr);
}