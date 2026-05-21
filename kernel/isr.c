#include "isr.h"
#include "idt.h"
#include "io.h"
#include "fault_handler.h"

void isr_handler(unsigned int num, unsigned int err) {
    fault_handler(num, err);
}

void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags) {
    idt_entries[num].base_lo = base & 0xFFFF;
    idt_entries[num].base_hi = (base >> 16) & 0xFFFF;
    idt_entries[num].sel = sel;
    idt_entries[num].always0 = 0;
    idt_entries[num].flags = flags;
}