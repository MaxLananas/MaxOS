#include "io.h"
#include "idt.h"

struct IDTEntry idt_entries[256];
struct IDTPtr idt_ptr;

void idt_init(void) {
    idt_ptr.limit = sizeof(struct IDTEntry) * 256 - 1;
    idt_ptr.base = (unsigned int)&idt_entries;

    // Initialisation manuelle sans memset
    for (unsigned int i = 0; i < 256; i++) {
        idt_entries[i].base_lo = 0;
        idt_entries[i].base_hi = 0;
        idt_entries[i].sel = 0;
        idt_entries[i].always0 = 0;
        idt_entries[i].flags = 0;
    }
}

void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags) {
    idt_entries[num].base_lo = (base & 0xFFFF);
    idt_entries[num].base_hi = (base >> 16) & 0xFFFF;
    idt_entries[num].sel = sel;
    idt_entries[num].always0 = 0;
    idt_entries[num].flags = flags;
}