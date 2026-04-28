#include "irq_handler.h"
#include "io.h"
#include "timer.h"
#include "keyboard.h"

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);

    if (num == 32) {
        timer_callback(0);
    } else if (num == 33) {
        keyboard_handler();
    }
}