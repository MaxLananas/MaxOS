#include "fault_handler.h"
#include "screen.h"
#include "isr.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("Fault handler called", 0x0C);
}

void fault_handler_init(void) {
    idt_set_gate(14, (unsigned int)isr14, 0x08, 0x8E);
}