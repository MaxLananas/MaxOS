#include "timer.h"
#include "io.h"
#include "irq.h"

unsigned int tick = 0;

void timer_callback(struct regs *r) {
    tick++;
}

void timer_init(unsigned int hz) {
    register_interrupt_handler(IRQ0, &timer_callback);
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
    while ((tick - start) * 1000 / 100 < ms);
}