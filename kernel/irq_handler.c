#include "irq.h"
#include "io.h"
#include "timer.h"
#include "keyboard.h"
#include "mouse.h"

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);

    if (interrupt_handlers[num] != 0) {
        isr_t handler = interrupt_handlers[num];
        handler(0);
    }
}