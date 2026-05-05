#include "io.h"
#include "idt.h"
#include "timer.h"
#include "screen.h"

extern void irq_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags);

static unsigned int timer_ticks = 0;

void timer_handler(void) {
    timer_ticks++;
}

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, (divisor >> 8) & 0xFF);

    irq_set_gate(32, (unsigned int)timer_handler, 0x08, 0x8E);
}

unsigned int timer_get_ticks(void) {
    return timer_ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start = timer_get_ticks();
    unsigned int end = start + (ms * 1000) / 1000;
    while (timer_get_ticks() < end);
}