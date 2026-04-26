#include "irq.h"
#include "idt.h"
#include "io.h"

void irq_install_handler(int irq, void (*handler)(void)) {
    (void)irq;
    (void)handler;
}

void irq_uninstall_handler(int irq) {
    (void)irq;
}