#include "timer.h"
#include "io.h"
#include "idt.h"
#include "isr.h"

unsigned int timer_ticks = 0;

void timer_handler(void) {
    timer_ticks++;
    outb(0x20, 0x20);
}

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, (divisor >> 8) & 0xFF);

    idt_set_gate(32, (unsigned int)isr32, 0x08, 0x8E);
    idt_load(&idt_ptr);
}

unsigned int timer_get_ticks(void) {
    return timer_ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start = timer_ticks;
    unsigned int wait = ms / 10;
    while ((timer_ticks - start) < wait);
}