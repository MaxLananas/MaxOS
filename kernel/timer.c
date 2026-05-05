#include "../kernel/timer.h"
#include "../kernel/io.h"
#include "../drivers/screen.h"

static unsigned int tick = 0;

static void timer_callback(void) {
    tick++;
}

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, (divisor >> 8) & 0xFF);
}

unsigned int timer_get_ticks(void) {
    return tick;
}

void timer_sleep(unsigned int ms) {
    unsigned int end = tick + ms;
    while (tick < end) {
        __asm__ volatile ("pause");
    }
}