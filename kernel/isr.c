#include "isr.h"
#include "screen.h"

static void (*handlers[48])(void) = {0};

void isr_install_handler(unsigned char num, void (*handler)(void)) {
    if (num < 48) {
        handlers[num] = handler;
    }
}

void isr_handler(unsigned int num, unsigned int err) {
    if (handlers[num]) {
        handlers[num]();
    } else {
        screen_writeln("Unhandled interrupt", 0x0C);
    }
}