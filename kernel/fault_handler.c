#include "fault_handler.h"
#include "screen.h"

void fault_handler(registers_t regs) {
    screen_writeln("Exception occurred", 0x0C);
}