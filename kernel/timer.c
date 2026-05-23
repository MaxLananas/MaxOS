#include "timer.h"
#include "io.h"
#include "isr.h"
#include "screen.h"

#define PIT_CHANNEL0_DATA 0x40
#define PIT_CMD_REGISTER 0x43

static unsigned int timer_ticks = 0;

void timer_init(unsigned int hz)
{
    unsigned int divisor = 1193180 / hz;

    outb(PIT_CMD_REGISTER, 0x36);
    outb(PIT_CHANNEL0_DATA, divisor & 0xFF);
    outb(PIT_CHANNEL0_DATA, (divisor >> 8) & 0xFF);

    screen_writeln("Timer initialized", 0x0A);
}

unsigned int timer_get_ticks(void)
{
    return timer_ticks;
}

void timer_sleep(unsigned int ms)
{
    unsigned int start = timer_ticks;
    while ((timer_ticks - start) < ms) {
        asm volatile("hlt");
    }
}

void timer_handler(void)
{
    timer_ticks++;
    outb(0x20, 0x20);
}