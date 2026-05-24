#include "timer.h"
#include "io.h"
#include "idt.h"

unsigned int ticks = 0;

void timer_callback(void) {
    ticks++;
}

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, (divisor >> 8) & 0xFF);

    idt_set_gate(32, (unsigned int)timer_callback, 0x08, 0x8E);
    idt_load(&idt_ptr);
}

unsigned int timer_get_ticks(void) {
    return ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start = ticks;
    unsigned int end = start + (ms * 1000) / 1000;
    while (ticks < end);
}