#include "fault_handler.h"
#include "screen.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("Fault occurred!", 0x0C);
    char num_str[4];
    num_str[0] = '0' + num / 100;
    num_str[1] = '0' + (num / 10) % 10;
    num_str[2] = '0' + num % 10;
    num_str[3] = 0;
    screen_writeln(num_str, 0x0C);
    while (1) {
        __asm__ volatile ("hlt");
    }
}