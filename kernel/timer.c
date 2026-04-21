#include "timer.h"
#include "io.h"

static unsigned int timer_ticks = 0;
static unsigned int timer_hz = 0;

void timer_handler(void) {
    timer_ticks++;
}

void timer_init(unsigned int hz) {
    timer_hz = hz;
    unsigned int divisor = 1193180 / hz;
    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, divisor >> 8);
}

unsigned int timer_get_ticks(void) {
    return timer_ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start = timer_get_ticks();
    while ((timer_get_ticks() - start) * (1000 / timer_hz) < ms) {
        asm volatile("pause");
    }
}