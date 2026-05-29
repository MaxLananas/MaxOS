#include "fault_handler.h"
#include "screen.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_set_color(0x0C);
    screen_writeln("EXCEPTION OCCURRED", 0x0C);
    screen_writeln("Exception number:", 0x0C);
    screen_putchar('0' + num / 10, 0x0C);
    screen_putchar('0' + num % 10, 0x0C);
    screen_writeln("", 0x0C);
    screen_writeln("Error code:", 0x0C);
    screen_putchar('0' + err / 10, 0x0C);
    screen_putchar('0' + err % 10, 0x0C);
    screen_writeln("", 0x0C);
    asm volatile("cli");
    asm volatile("hlt");
}