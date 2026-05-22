#include "timer.h"
#include "io.h"
#include "idt.h"
#include "screen.h"

#define PIT_CHANNEL0 0x40
#define PIT_CMD 0x43

static unsigned int ticks = 0;

void timer_callback(void) {
    ticks++;
}

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;

    outb(PIT_CMD, 0x36);
    outb(PIT_CHANNEL0, divisor & 0xFF);
    outb(PIT_CHANNEL0, (divisor >> 8) & 0xFF);

    idt_set_gate(32, (unsigned int)isr32, 0x08, 0x8E);
    outb(0x21, inb(0x21) & ~(1 << 0));
}

unsigned int timer_get_ticks(void) {
    return ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start = ticks;
    unsigned int end = start + (ms * 1000) / 1000; // Convert ms to ticks
    while (ticks < end);
}