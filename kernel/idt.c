#include "idt.h"
#include "../drivers/screen.h"
#include "../kernel/io.h"

struct IDTEntry idt[256];
struct IDTPtr idtp;

void idt_init(void) {
    idtp.limit = sizeof(struct IDTEntry) * 256 - 1;
    idtp.base = (unsigned int)&idt;

    mem_init(1024 * 1024);
    idt_load(&idtp);
}

void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags) {
    idt[num].base_lo = base & 0xFFFF;
    idt[num].base_hi = (base >> 16) & 0xFFFF;
    idt[num].sel = sel;
    idt[num].always0 = 0;
    idt[num].flags = flags;
}