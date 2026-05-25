#include "isr.h"
#include "screen.h"
#include "io.h"

extern void *memcpy(void *dest, const void *src, unsigned int n);

void isr_handler(unsigned int num, unsigned int err) {
    screen_set_color(0x0C);
    screen_writeln("INTERRUPT: ", 0x0C);
    screen_putchar('0' + num / 10, 0x0C);
    screen_putchar('0' + num % 10, 0x0C);
    screen_writeln("", 0x0C);
    for(;;);
}