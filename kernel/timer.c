#include "timer.h"
#include "io.h"
#include "idt.h"
#include "screen.h"

static unsigned int timer_ticks = 0;

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, (divisor >> 8) & 0xFF);

    idt_set_gate(32, (unsigned int)isr32, 0x08, 0x8E);
    outb(0x21, inb(0x21) & 0xFE);
}

void timer_handler(void) {
    timer_ticks++;
    outb(0x20, 0x20);
}

unsigned int timer_get_ticks(void) {
    return timer_ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start = timer_ticks;
    while ((timer_ticks - start) * 1000 / 100 < ms) {
        asm volatile("hlt");
    }
}