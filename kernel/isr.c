#include "isr.h"
#include "fault_handler.h"
#include "screen.h"

void isr_handler(unsigned int num, unsigned int err)
{
    screen_writeln("Interrupt occurred", 0x0C);
    fault_handler(num, err);
}