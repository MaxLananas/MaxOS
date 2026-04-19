#include "timer.h"
#include "io.h"
#include "idt.h"

void timer_handler() {
}

void timer_init() {
    outb(0x43, 0x36);
    outb(0x40, 0x9C);
    outb(0x40, 0x2E);
}