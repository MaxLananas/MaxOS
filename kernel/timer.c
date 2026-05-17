#include "timer.h"
#include "io.h"
#include "screen.h"
#include "idt.h"

static unsigned int ticks = 0;

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, (divisor >> 8) & 0xFF);

    idt_set_gate(32, (unsigned int)timer_handler, 0x08, 0x8E);
    outb(0x21, inb(0x21) & 0xFE);
}

unsigned int timer_get_ticks(void) {
    return ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start = ticks;
    unsigned int end = start + ms * 1000 / 18;
    while (ticks < end) {
        asm volatile("hlt");
    }
}

void timer_handler(void) {
    ticks++;
    outb(0x20, 0x20);
}