#include "irq.h"
#include "idt.h"
#include "io.h"
#include "timer.h"
#include "keyboard.h"
#include "mouse.h"

extern void irq0();
extern void irq1();
extern void irq12();

void irq_init() {
    idt_set_gate(32, (unsigned int)irq0, 0x08, 0x8E);
    idt_set_gate(33, (unsigned int)irq1, 0x08, 0x8E);
    idt_set_gate(44, (unsigned int)irq12, 0x08, 0x8E);
}

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);

    if (num == 32) {
        timer_callback();
    } else if (num == 33) {
        keyboard_handler();
    } else if (num == 44) {
        mouse_handler();
    }
}