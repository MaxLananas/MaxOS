#include "screen.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("Fault occurred!", 0x0C);
    screen_writeln("Interrupt number:", 0x0C);
    char num_str[16];
    num_str[0] = '0' + (num / 10);
    num_str[1] = '0' + (num % 10);
    num_str[2] = 0;
    screen_writeln(num_str, 0x0C);
    while (1) {
        asm volatile("hlt");
    }
}