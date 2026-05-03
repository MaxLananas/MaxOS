#include "irq_handler.h"
#include "io.h"

void irq_install_handler(int irq, void (*handler)(void)) {
    // Install IRQ handler
}

void irq_uninstall_handler(int irq) {
    // Uninstall IRQ handler
}

void irq_handler(unsigned int num) {
    // Common IRQ handler
}