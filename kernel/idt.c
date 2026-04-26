#include "idt.h"
#include "io.h"
#include "isr.h"

struct IDTEntry idt[256];
struct IDTPtr idtp;

void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags) {
    idt[num].base_lo = (base & 0xFFFF);
    idt[num].base_hi = (base >> 16) & 0xFFFF;
    idt[num].sel = sel;
    idt[num].always0 = 0;
    idt[num].flags = flags;
}

void idt_load(void) {
    idtp.limit = (sizeof(struct IDTEntry) * 256) - 1;
    idtp.base = (unsigned int)&idt;
    __asm__ __volatile__("lidt (%0)" : : "r" (&idtp));
}

void idt_init(void) {
    for (int i = 0; i < 256; i++) {
        idt_set_gate(i, 0, 0x08, 0x8E);
    }
    idt_load();
}