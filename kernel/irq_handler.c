#include "idt.h"
#include "io.h"
#include "timer.h"
#include "keyboard.h"
#include "mouse.h"

extern void irq_install(void);

void *irq_routines[16] = {
    0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0
};

void irq_set_handler(unsigned int irq, void (*handler)(void)) {
    irq_routines[irq] = handler;
}

void irq_handler(unsigned int num) {
    void (*handler)(void);
    handler = irq_routines[num - 32];
    if (handler) {
        handler();
    }
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}

void irq_init(void) {
    irq_install();
    outb(0x21, 0xFF);
    outb(0xA1, 0xFF);
    __asm__ volatile("sti");
}