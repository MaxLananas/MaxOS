#include "timer.h"
#include "io.h"
#include "irq.h"

unsigned int tick = 0;

void timer_handler(void) {
    tick++;
    outb(0x20, 0x20);
}

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, (divisor >> 8) & 0xFF);
}

unsigned int timer_get_ticks(void) {
    return tick;
}

void timer_sleep(unsigned int ms) {
    unsigned int start = tick;
    unsigned int end = start + (ms * 1000) / 1000;
    while (tick < end);
}