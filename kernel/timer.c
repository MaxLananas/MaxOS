#include "timer.h"
#include "io.h"
#include "screen.h"
#include "terminal.h"

static unsigned int timer_ticks = 0;

void timer_handler(void) {
    timer_ticks++;
}

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, (divisor >> 8) & 0xFF);
}

unsigned int timer_get_ticks(void) {
    return timer_ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start = timer_get_ticks();
    unsigned int end = start + ms * 100 / 1193;
    while (timer_get_ticks() < end);
}