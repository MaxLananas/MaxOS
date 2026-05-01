#include "io.h"
#include "irq_handler.h"

void (*irq_routines[16])(void) = {0};

void irq_handler(unsigned int num) {
    void (*handler)(void);
    handler = irq_routines[num - 32];
    if (handler != 0) {
        handler();
    }
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}