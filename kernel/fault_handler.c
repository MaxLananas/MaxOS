#include "fault_handler.h"
#include "screen.h"
#include "idt.h"

void fault_handler(registers_t regs) {
    screen_writeln("Exception occurred!", 0x0C);
    screen_writeln("System halted", 0x0C);
    while (1);
}