#include "isr.h"
#include "idt.h"
#include "screen.h"
#include "io.h"

void *irq_routines[16] = {0};

void isr_handler(unsigned int num, unsigned int err) {
    screen_write("Received interrupt: ", 0x0F);
    screen_putchar('0' + num / 10, 0x0F);
    screen_putchar('0' + num % 10, 0x0F);
    screen_putchar('\n', 0x0F);
}

void irq_handler(unsigned int num) {
    if (num >= 40) outb(0xA0, 0x20);
    outb(0x20, 0x20);

    if (irq_routines[num] != 0) {
        void (*handler)(unsigned int) = irq_routines[num];
        handler(num);
    }
}

void irq_install_handler(unsigned int irq, void (*handler)(unsigned int)) {
    irq_routines[irq] = handler;
}

void irq_uninstall_handler(unsigned int irq) {
    irq_routines[irq] = 0;
}