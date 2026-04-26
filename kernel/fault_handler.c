#include "fault_handler.h"
#include "screen.h"
#include "io.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_set_color(0x0C);
    screen_writeln("EXCEPTION: ", 0x0C);
    screen_putchar('0' + num / 10, 0x0C);
    screen_putchar('0' + num % 10, 0x0C);
    screen_writeln("", 0x0C);

    for(;;);
}