#include "timer.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

static unsigned int ticks = 0;

void timer_handler(void) {
    ticks++;
}

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, (divisor >> 8) & 0xFF);

    irq_set_handler(0, timer_handler);
}

unsigned int timer_get_ticks(void) {
    return ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start = ticks;
    unsigned int wait = ms * 1000 / 1000; // Approximate conversion
    while (ticks - start < wait);
}