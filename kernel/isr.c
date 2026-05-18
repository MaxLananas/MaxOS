#include "isr.h"
#include "idt.h"
#include "io.h"
#include "screen.h"

isr_t interrupt_handlers[256];

void register_interrupt_handler(unsigned char n, isr_t handler) {
    interrupt_handlers[n] = handler;
}

void isr_handler(unsigned int num, unsigned int err) {
    if (interrupt_handlers[num] != 0) {
        isr_t handler = interrupt_handlers[num];
        handler(num, err);
    } else {
        screen_writeln("Unhandled exception", 0x0F);
        screen_writeln("Exception number: ", 0x0F);
        screen_putchar('0' + num / 10, 0x0F);
        screen_putchar('0' + num % 10, 0x0F);
        for(;;);
    }
}
```=== END FILE ===