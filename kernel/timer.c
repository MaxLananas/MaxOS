#include "timer.h"
#include "io.h"
#include "idt.h"
#include "screen.h"

#define PIT_CHANNEL0 0x40
#define PIT_CMD 0x43

static unsigned int ticks = 0;

void timer_init(unsigned int hz)
{
    unsigned int divisor = 1193180 / hz;

    outb(PIT_CMD, 0x36);
    outb(PIT_CHANNEL0, divisor & 0xFF);
    outb(PIT_CHANNEL0, (divisor >> 8) & 0xFF);

    idt_set_gate(32, (unsigned int)isr32, 0x08, 0x8E);
    outb(0x21, inb(0x21) & 0xFE);
}

void timer_handler(void)
{
    ticks++;
    outb(0x20, 0x20);
}

unsigned int timer_get_ticks(void)
{
    return ticks;
}

void timer_sleep(unsigned int ms)
{
    unsigned int start = ticks;
    unsigned int end = start + ms * 100 / 1193;

    while (ticks < end) {
        asm volatile("hlt");
    }
}