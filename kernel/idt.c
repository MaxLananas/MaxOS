#include "idt.h"

void idt_init(void) {
}

void register_interrupt_handler(unsigned char n, void (*handler)(struct registers* regs)) {
    (void)n;
    (void)handler;
}