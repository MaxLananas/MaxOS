#include "isr.h"
#include "screen.h"
#include "fault_handler.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_writeln("Received interrupt", 0x0C);
    fault_handler(num, err);
}