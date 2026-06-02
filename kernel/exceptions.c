#include "fault_handler.h"
#include "screen.h"
#include "idt.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_writeln("Received exception", 0x0C);
    fault_handler(num, err);
}

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("Fault handler called", 0x0C);
    while (1);
}