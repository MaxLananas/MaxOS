#include "irq.h"
#include "io.h"
#include "idt.h"

void irq_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags) {
    idt_set_gate(num + 32, base, sel, flags);
}