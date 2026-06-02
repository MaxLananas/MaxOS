#include "timer.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

static unsigned int ticks = 0;

void timer_handler(void) {
    ticks++;
}

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;

    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, (divisor >> 8) & 0xFF);

    irq_install_handler(0, timer_handler);
    screen_writeln("Timer initialized", 0x0F);
}

unsigned int timer_get_ticks(void) {
    return ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start_ticks = ticks;
    unsigned int end_ticks = start_ticks + (ms * 100) / 1193;

    while (ticks < end_ticks) {
        asm volatile("hlt");
    }
}