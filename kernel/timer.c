#include "timer.h"
#include "io.h"

#define PIT_CH0 0x40
#define PIT_CMD 0x43
#define PIT_IRQ 0

static unsigned int timer_ticks_count = 0;

void timer_init(void) {
    unsigned int divisor = 1193180 / 1000;
    outb(PIT_CMD, 0x36);
    outb(PIT_CH0, divisor & 0xFF);
    outb(PIT_CH0, (divisor >> 8) & 0xFF);
}

unsigned int timer_ticks(void) {
    return timer_ticks_count;
}

void sleep_ms(unsigned int ms) {
    unsigned int start = timer_ticks_count;
    while ((timer_ticks_count - start) < ms) {
        asm volatile("hlt");
    }
}

void timer_handler(void) {
    timer_ticks_count++;
}