#include "timer.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

unsigned int ticks = 0;

void timer_callback(void) {
    ticks++;
}

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;

    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, (divisor >> 8) & 0xFF);

    irq_install_handler(0, timer_callback);
}

unsigned int timer_get_ticks(void) {
    return ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start = ticks;
    while ((ticks - start) * 1000 / 100 < ms) {
        __asm__ __volatile__("hlt");
    }
}