#include "idt.h"
#include "io.h"

#define IDT_ENTRIES 256

struct IDTEntry idt[IDT_ENTRIES];
struct IDTPtr idtp;

void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags) {
    idt[num].base_lo = base & 0xFFFF;
    idt[num].base_hi = (base >> 16) & 0xFFFF;
    idt[num].sel = sel;
    idt[num].always0 = 0;
    idt[num].flags = flags;
}

void idt_init(void) {
    idtp.limit = (sizeof(struct IDTEntry) * IDT_ENTRIES) - 1;
    idtp.base = (unsigned int)&idt;

    for (int i = 0; i < IDT_ENTRIES; i++) {
        idt_set_gate(i, 0, 0, 0);
    }

    idt_load();
}