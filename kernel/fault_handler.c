#include "fault_handler.h"
#include "screen.h"
#include "idt.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("Exception occurred!", 0x0C);
    screen_writeln("Number:", 0x0C);
    screen_putchar('0' + num / 10, 0x0C);
    screen_putchar('0' + num % 10, 0x0C);
    screen_writeln("", 0x0C);
    screen_writeln("Error code:", 0x0C);
    screen_putchar('0' + err / 10, 0x0C);
    screen_putchar('0' + err % 10, 0x0C);
    screen_writeln("", 0x0C);
    asm volatile("cli");
    while (1) {
        asm volatile("hlt");
    }
}