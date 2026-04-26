#include "irq.h"
#include "screen.h"
#include "timer.h"
#include "keyboard.h"

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);

    if (num == 32) {
        timer_handler();
    } else if (num == 33) {
        keyboard_handler();
    }
}