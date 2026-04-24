#include "idt.h"
#include "io.h"
#include "irq_handler.h"

void irq_install_handler(unsigned char irq, void (*handler)(void)) {
    idt_set_gate(32 + irq, (unsigned int)handler, 0x08, 0x8E);
}

void irq_uninstall_handler(unsigned char irq) {
    idt_set_gate(32 + irq, 0, 0, 0);
}