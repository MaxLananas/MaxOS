#include "irq.h"
#include "idt.h"
#include "io.h"
#include "keyboard.h"
#include "timer.h"
#include "mouse.h"

void irq_handler(unsigned int num) {
    if (num == 32) {
        timer_callback();
    } else if (num == 33) {
        keyboard_handler();
    } else if (num == 44) {
        mouse_handler();
    }
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}