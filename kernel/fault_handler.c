#include "fault_handler.h"
#include "screen.h"
#include "isr.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("Exception occurred!", 0x04);
    screen_write("Exception number: ", 0x04);
    screen_putchar('0' + num, 0x04);
    screen_writeln("", 0x04);

    while (1) {
        asm volatile("hlt");
    }
}