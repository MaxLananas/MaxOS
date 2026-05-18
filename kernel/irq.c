#include "irq.h"
#include "idt.h"
#include "io.h"
#include "screen.h"

isr_t interrupt_handlers[256];

void register_interrupt_handler(unsigned char n, isr_t handler) {
    interrupt_handlers[n] = handler;
}

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);

    if (interrupt_handlers[num] != 0) {
        isr_t handler = interrupt_handlers[num];
        handler(num);
    }
}
```=== END FILE ===