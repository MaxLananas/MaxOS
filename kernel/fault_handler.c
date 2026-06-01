#include "fault_handler.h"
#include "screen.h"
#include "idt.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("Exception occurred!", 0x0C);
    screen_writeln("System Halted", 0x0C);
    for (;;);
}