#include "timer.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

#define PIT_CHANNEL0_DATA 0x40
#define PIT_COMMAND_PORT 0x43

static unsigned int ticks = 0;

void timer_init(unsigned int hz)
{
    unsigned int divisor = 1193180 / hz;

    outb(PIT_COMMAND_PORT, 0x36);
    outb(PIT_CHANNEL0_DATA, divisor & 0xFF);
    outb(PIT_CHANNEL0_DATA, (divisor >> 8) & 0xFF);

    screen_writeln("Timer initialized", 0x0A);
}

unsigned int timer_get_ticks(void)
{
    return ticks;
}

void timer_sleep(unsigned int ms)
{
    unsigned int start_ticks = ticks;
    unsigned int end_ticks = start_ticks + (ms * 100) / 1193;

    while (ticks < end_ticks) {
        asm volatile("hlt");
    }
}

void timer_handler(void)
{
    ticks++;
}