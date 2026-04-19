#include "timer.h"
#include "io.h"
#include "idt.h"

volatile unsigned int g_ticks = 0;

void timer_handler() {
    g_ticks++;
    outb(0x20, 0x20);
}

void timer_init() {
    unsigned short divisor = 11931;
    outb(0x43, 0x36);
    outb(0x40, divisor & 0xFF);
    outb(0x40, (divisor >> 8) & 0xFF);
    idt_set_gate(32, (unsigned int)timer_handler, 0x08, 0x8E);
    outb(0x21, inb(0x21) & ~0x01);
}