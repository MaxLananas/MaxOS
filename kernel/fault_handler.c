#include "fault_handler.h"
#include "screen.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("Fault occurred", 0x0C);
}