#include "io.h"
#include "isr.h"
#include "timer.h"

static unsigned int ticks = 0;

void timer_callback(void) {
    ticks++;
}

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, divisor >> 8);
}

unsigned int timer_get_ticks(void) {
    return ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int end = ticks + ms;
    while (ticks < end) {
        __asm__ volatile ("pause");
    }
}