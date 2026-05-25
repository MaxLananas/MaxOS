#include "irq.h"
#include "screen.h"
#include "io.h"
#include "timer.h"
#include "keyboard.h"
#include "mouse.h"

void *memcpy(void *dest, const void *src, unsigned int n);

void irq_handler(unsigned int num) {
    if(num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);

    switch(num) {
        case 0:
            timer_callback();
            break;
        case 1:
            keyboard_handler();
            break;
        case 12:
            mouse_handler();
            break;
    }
}