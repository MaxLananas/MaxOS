#include "irq.h"
#include "../kernel/io.h"

void irq_install_handler(int irq, void (*handler)(void)) {
    (void)irq;
    (void)handler;
}