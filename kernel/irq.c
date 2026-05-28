#include "irq.h"
#include "io.h"
#include "screen.h"
#include "timer.h"
#include "keyboard.h"
#include "mouse.h"

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);

    switch(num) {
        case 32: timer_handler(); break;
        case 33: keyboard_handler(); break;
        case 44: mouse_handler(); break;
        default: break;
    }
}