#include "isr.h"
#include "idt.h"
#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "fault_handler.h"

void isr_handler(unsigned int num, unsigned int err) {
    if (num < 32) {
        fault_handler(num, err);
    } else {
        irq_handler(num - 32);
    }
}

void irq_handler(unsigned int num) {
    if (num == 0) {
        timer_handler();
    } else if (num == 1) {
        keyboard_handler();
    }
    if (num >= 8) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}