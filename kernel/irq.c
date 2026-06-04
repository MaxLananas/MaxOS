#include "idt.h"
#include "io.h"
#include "irq.h"
#include "timer.h"
#include "keyboard.h"
#include "mouse.h"

void irq_handler(unsigned int num)
{
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);

    if (num == 32) {
        timer_handler();
    } else if (num == 33) {
        keyboard_handler();
    } else if (num == 44) {
        mouse_handler();
    }
}

void irq_init(void)
{
    outb(0x21, 0xFC);
    outb(0xA1, 0xFF);
}