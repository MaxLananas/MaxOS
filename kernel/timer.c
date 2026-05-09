#include "kernel/io.h"
#include "kernel/timer.h"
#include "kernel/idt.h"
#include "drivers/screen.h"

#define PIT_DATA_PORT 0x40
#define PIT_COMMAND_PORT 0x43

static unsigned int timer_ticks = 0;

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;
    outb(PIT_COMMAND_PORT, 0x36);
    outb(PIT_DATA_PORT, divisor & 0xFF);
    outb(PIT_DATA_PORT, (divisor >> 8) & 0xFF);

    idt_set_gate(32, (unsigned int)timer_handler, 0x08, 0x8E);
    screen_writeln("Timer initialized", 0x0A);
}

unsigned int timer_get_ticks(void) {
    return timer_ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start = timer_ticks;
    while ((timer_ticks - start) * 10 < ms);
}

void timer_handler(void) {
    timer_ticks++;
}