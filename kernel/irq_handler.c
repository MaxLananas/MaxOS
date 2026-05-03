#include "irq_handler.h"
#include "screen.h"
#include "io.h"

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);

    if (num == 33) {
        keyboard_handler();
    } else if (num == 44) {
        mouse_handler();
    }
}