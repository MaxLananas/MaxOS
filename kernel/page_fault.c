#include "page_fault.h"
#include "screen.h"

void page_fault_handler(unsigned int addr) {
    screen_clear();
    screen_writeln("PAGE FAULT OCCURRED!", 0x0C);
    screen_writeln("Address: ", 0x0F);
    screen_putchar('0' + addr, 0x0F);
    screen_putchar('\n', 0x0F);

    while(1);
}