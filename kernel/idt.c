#include "idt.h"
#include "io.h"

struct IDTEntry idt_entries[256];
struct IDTPtr idt_ptr;

void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags) {
    idt_entries[num].base_lo = base & 0xFFFF;
    idt_entries[num].base_hi = (base >> 16) & 0xFFFF;
    idt_entries[num].sel = sel;
    idt_entries[num].always0 = 0;
    idt_entries[num].flags = flags;
}

void idt_load(struct IDTPtr *idt_ptr) {
    __asm__ volatile("lidt %0" :: "m"(*idt_ptr));
}