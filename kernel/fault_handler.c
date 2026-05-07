#include "fault_handler.h"
#include "screen.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("Exception occurred", 0x0C);
    screen_writeln("Number:", 0x0C);
    screen_putchar('0' + num, 0x0C);
    screen_writeln("Error code:", 0x0C);
    screen_putchar('0' + err, 0x0C);
    while (1) {
        asm volatile("hlt");
    }
}