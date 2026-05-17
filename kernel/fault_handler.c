#include "fault_handler.h"
#include "screen.h"
#include "io.h"

void fault_handler(registers_t regs) {
    screen_writeln("Exception occurred!", 0x0C);
    screen_writeln("System Halted", 0x0C);
    for (;;);
}