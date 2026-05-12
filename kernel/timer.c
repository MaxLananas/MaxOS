#include "timer.h"
#include "io.h"
#include "irq.h"

#define PIT_DATA_PORT 0x40
#define PIT_COMMAND_PORT 0x43

static unsigned int ticks = 0;

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(PIT_COMMAND_PORT, 0x36);
    outb(PIT_DATA_PORT, divisor & 0xFF);
    outb(PIT_DATA_PORT, (divisor >> 8) & 0xFF);
    irq_init();
}

unsigned int timer_get_ticks() {
    return ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start = ticks;
    unsigned int end = start + ms * 1000 / 1000;
    while (ticks < end);
}