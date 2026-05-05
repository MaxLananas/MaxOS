#include "timer.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

static unsigned int ticks = 0;

void timer_handler(unsigned int num) {
    ticks++;
}

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, (divisor >> 8) & 0xFF);
    irq_clear_mask(0);
}

unsigned int timer_get_ticks(void) {
    return ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start = ticks;
    unsigned int end = start + (ms * 100) / 1000;
    while (ticks < end);
}