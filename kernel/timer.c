#include "timer.h"
#include "io.h"
#include "screen.h"

static unsigned int tick = 0;

void timer_handler();

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, divisor >> 8);
    outb(0x21, 0xFE);
}

unsigned int timer_get_ticks() {
    return tick;
}

void timer_sleep(unsigned int ms) {
    unsigned int end = tick + ms;
    while (tick < end) {
        asm volatile ("hlt");
    }
}