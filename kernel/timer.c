#include "drivers/screen.h"
#include "kernel/io.h"
#include "kernel/idt.h"
#include "kernel/timer.h"

#define PIT_DATA_PORT 0x40
#define PIT_COMMAND_PORT 0x43
#define PIT_IRQ 0

static unsigned int timer_ticks = 0;

void timer_init(unsigned int hz) {
    unsigned int divisor = 1193180 / hz;

    outb(PIT_COMMAND_PORT, 0x36);
    outb(PIT_DATA_PORT, divisor & 0xFF);
    outb(PIT_DATA_PORT, (divisor >> 8) & 0xFF);

    idt_set_gate(32, (unsigned int)timer_handler, 0x08, 0x8E);
    outb(0x21, inb(0x21) & 0xFE);
}

unsigned int timer_get_ticks(void) {
    return timer_ticks;
}

void timer_sleep(unsigned int ms) {
    unsigned int start_ticks = timer_ticks;
    unsigned int ticks_to_wait = ms * 100 / 182;

    while ((timer_ticks - start_ticks) < ticks_to_wait) {
        asm volatile("hlt");
    }
}

void timer_handler(void) {
    timer_ticks++;
    outb(0x20, 0x20);
}