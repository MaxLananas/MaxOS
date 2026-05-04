#include "irq_handler.h"
#include "io.h"
#include "screen.h"
#include "timer.h"
#include "keyboard.h"
#include "mouse.h"

void *irq_routines[16] = {0};

void irq_handler(unsigned int num) {
    if (irq_routines[num] != 0) {
        void (*handler)(void) = irq_routines[num];
        handler();
    }

    if (num >= 8) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}

void irq_install_handler(int irq, void (*handler)(void)) {
    irq_routines[irq] = handler;
}

void irq_uninstall_handler(int irq) {
    irq_routines[irq] = 0;
}