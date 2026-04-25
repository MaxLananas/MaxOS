#include "io.h"

void irq_send_eoi(unsigned int irq) {
    if (irq >= 8) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}