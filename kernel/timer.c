#include "kernel/timer.h"
#include "kernel/idt.h"
#include "kernel/io.h"
#include "kernel/isr.h"

static volatile unsigned int ticks = 0;

static void timer_callback(struct registers *regs) {
    (void)regs;
    ticks++;
}

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(0x43, 0x36);
    outb(0x40, (unsigned char)(divisor & 0xFF));
    outb(0x40, (unsigned char)((divisor >> 8) & 0xFF));
    idt_set_gate(32, (unsigned int)isr32, 0x08, 0x8E);
    outb(0x21, inb(0x21) & ~0x01);
}

unsigned int timer_get_ticks(void) {
    return ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int end = ticks + ms;
    while (ticks < end) {
        __asm__ volatile("hlt");
    }
}
