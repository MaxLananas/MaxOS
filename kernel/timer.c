#include "timer.h"
#include "io.h"
#include "screen.h"

#define PIT_CMD_PORT 0x43
#define PIT_DATA_PORT 0x40

static unsigned int timer_ticks = 0;

void timer_handler(void) {
    timer_ticks++;
    outb(0x20, 0x20);
}

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;

    outb(PIT_CMD_PORT, 0x36);
    outb(PIT_DATA_PORT, divisor & 0xFF);
    outb(PIT_DATA_PORT, (divisor >> 8) & 0xFF);

    screen_writeln("Timer initialized", 0x0A);
}

unsigned int timer_get_ticks(void) {
    return timer_ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start_ticks = timer_ticks;
    while ((timer_ticks - start_ticks) * 1000 / 100 < ms);
}