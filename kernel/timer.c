#include "timer.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

unsigned int timer_ticks = 0;

void timer_callback(struct regs *r) {
    timer_ticks++;
}

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, (divisor >> 8) & 0xFF);
    irq_set_handler(0, timer_callback);
}

unsigned int timer_get_ticks(void) {
    return timer_ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int end = timer_ticks + ms;
    while (timer_ticks < end);
}