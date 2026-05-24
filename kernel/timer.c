#include "timer.h"
#include "idt.h"
#include "io.h"
#include "screen.h"

unsigned int ticks = 0;

void timer_callback() {
    ticks++;
}

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, (divisor >> 8) & 0xFF);
    idt_set_gate(32, (unsigned int)irq0, 0x08, 0x8E);
}

unsigned int timer_get_ticks(void) {
    return ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start = ticks;
    unsigned int end = start + ms;
    while (ticks < end)
        asm volatile("hlt");
}