#include "kernel/irq.h"
#include "kernel/io.h"
#include "drivers/keyboard.h"

void irq_handler(unsigned int num) {
    if (num >= 32 && num < 48) {
        if (num == 33) {
            keyboard_handler();
        }
        if (num >= 40) {
            outb(0xA0, 0x20);
        }
        outb(0x20, 0x20);
    }
}