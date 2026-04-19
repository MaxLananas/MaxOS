#include "timer.h"
#include "idt.h"

extern void outb(unsigned short port, unsigned char data);
extern unsigned char inb(unsigned short port);

volatile unsigned int ticks = 0;

void timer_handler(struct registers* regs) {
    (void)regs;
    ticks++;
}

void timer_init(void) {
    unsigned int divisor = 11931;

    register_interrupt_handler(32, timer_handler);

    outb(0x43, 0x36);
    outb(0x40, (unsigned char)(divisor & 0xFF));
    outb(0x40, (unsigned char)((divisor >> 8) & 0xFF));
}

unsigned int timer_ticks(void) {
    return ticks;
}

void sleep_ms(unsigned int ms) {
    unsigned int start_ticks = ticks;
    unsigned int end_ticks = start_ticks + ms / 10;

    while (ticks < end_ticks) {
        __asm__ volatile("hlt");
    }
}