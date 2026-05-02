#include "timer.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

#define PIT_CHANNEL0 0x40
#define PIT_COMMAND 0x43

static unsigned int timer_ticks = 0;

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(PIT_COMMAND, 0x36);
    outb(PIT_CHANNEL0, divisor & 0xFF);
    outb(PIT_CHANNEL0, (divisor >> 8) & 0xFF);
    screen_writeln("Timer initialized", 0x0A);
}

unsigned int timer_get_ticks(void) {
    return timer_ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start = timer_ticks;
    while ((timer_ticks - start) * 10 < ms);
}