#include "fault_handler.h"
#include "screen.h"
#include "io.h"

void fault_handler(unsigned int num, unsigned int err)
{
    screen_writeln("Fault:", 0x04);
    screen_write("Num: ", 0x04);
    screen_putchar('0' + (num / 10), 0x04);
    screen_putchar('0' + (num % 10), 0x04);
    screen_putchar('\n', 0x04);

    outb(0x20, 0x20);
}