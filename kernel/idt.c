#include "idt.h"
#include "io.h"

struct IDTEntry idt_entries[256];
struct IDTPtr idtp;

void idt_init(void) {
    idtp.limit = sizeof(struct IDTEntry) * 256 - 1;
    idtp.base = (unsigned int)&idt_entries;

    for (int i = 0; i < 256; i++) {
        idt_set_gate(i, 0, 0x08, 0x8E);
    }

    idt_load(&idtp);
}

void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags) {
    idt_entries[num].base_lo = base & 0xFFFF;
    idt_entries[num].base_hi = (base >> 16) & 0xFFFF;
    idt_entries[num].sel = sel;
    idt_entries[num].always0 = 0;
    idt_entries[num].flags = flags;
}

void idt_load(struct IDTPtr *idtp) {
    __asm__ volatile("lidt %0" :: "m"(*idtp));
}