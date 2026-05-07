#include "fault_handler.h"
#include "../drivers/screen.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("CPU Exception:", 0x04);
    screen_putchar('0' + num / 10, 0x04);
    screen_putchar('0' + num % 10, 0x04);
    screen_writeln("", 0x04);
    while(1);
}