#include "timer.h"
#include "io.h"
#include "screen.h"
#include "isr.h"

#define PIT_DATA_PORT 0x40
#define PIT_COMMAND_PORT 0x43

static unsigned int ticks = 0;

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(PIT_COMMAND_PORT, 0x36);
    outb(PIT_DATA_PORT, divisor & 0xFF);
    outb(PIT_DATA_PORT, (divisor >> 8) & 0xFF);
    screen_writeln("Timer initialized", 0x09);
}

unsigned int timer_get_ticks(void) {
    return ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start_ticks = ticks;
    unsigned int end_ticks = start_ticks + (ms * 1000) / 1000;
    while (ticks < end_ticks) {
        asm volatile("hlt");
    }
}

void timer_handler(void) {
    ticks++;
}