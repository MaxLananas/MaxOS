#include "timer.h"
#include "io.h"
#include "irq.h"

#define PIT_CHANNEL0 0x40
#define PIT_CMD 0x43

static unsigned int ticks = 0;

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(PIT_CMD, 0x36);
    outb(PIT_CHANNEL0, divisor & 0xFF);
    outb(PIT_CHANNEL0, (divisor >> 8) & 0xFF);
    irq_install_handler(0, timer_handler);
}

unsigned int timer_get_ticks(void) {
    return ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start = ticks;
    unsigned int end = start + ms * 1000 / 1000;
    while (ticks < end) {
        asm volatile("hlt");
    }
}

void timer_handler(void) {
    ticks++;
    outb(0x20, 0x20);
}