#include "timer.h"
#include "io.h"

#define PIT_CH0 0x40
#define PIT_CMD 0x43
#define PIT_IRQ 0

volatile unsigned int g_ticks = 0;

void timer_init(void) {
    unsigned int divisor = 11931;
    outb(PIT_CMD, 0x36);
    outb(PIT_CH0, divisor & 0xFF);
    outb(PIT_CH0, (divisor >> 8) & 0xFF);
}

unsigned int timer_ticks(void) {
    return g_ticks;
}

void sleep_ms(unsigned int ms) {
    unsigned int start = g_ticks;
    while ((g_ticks - start) < ms) {
        asm volatile("hlt");
    }
}

void timer_handler(void) {
    g_ticks++;
    outb(0x20, 0x20);
}