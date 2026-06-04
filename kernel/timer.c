#include "timer.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

static unsigned int timer_ticks = 0;

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, (divisor >> 8) & 0xFF);
    irq_set_gate(0, (unsigned int)irq0, 0x08, 0x8E);
}

unsigned int timer_get_ticks(void) {
    return timer_ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start_ticks = timer_ticks;
    unsigned int ticks_to_wait = ms * 100 / 1193;

    while ((timer_ticks - start_ticks) < ticks_to_wait) {
        asm volatile("hlt");
    }
}

void timer_handler(void) {
    timer_ticks++;
    outb(0x20, 0x20);
}