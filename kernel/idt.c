#include "idt.h"
#include "io.h"

struct IDTEntry idt[256];
struct IDTPtr idtp;

extern void idt_load(void);
extern void *isr_stub_table[];

void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags) {
    idt[num].base_lo = (base & 0xFFFF);
    idt[num].base_hi = (base >> 16) & 0xFFFF;
    idt[num].sel = sel;
    idt[num].always0 = 0;
    idt[num].flags = flags;
}

void idt_init(void) {
    idtp.limit = (sizeof(struct IDTEntry) * 256) - 1;
    idtp.base = (unsigned int)&idt;

    for (unsigned int i = 0; i < 32; i++) {
        idt_set_gate(i, (unsigned int)isr_stub_table[i], 0x08, 0x8E);
    }

    for (unsigned int i = 32; i < 48; i++) {
        idt_set_gate(i, (unsigned int)isr_stub_table[i], 0x08, 0x8E);
    }

    idt_load();
}