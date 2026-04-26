#include "isr.h"
#include "idt.h"
#include "io.h"
#include "fault_handler.h"

isr_t interrupt_handlers[256];

void register_interrupt_handler(unsigned char n, isr_t handler) {
    interrupt_handlers[n] = handler;
}

void isr_handler(unsigned int num, unsigned int err) {
    if (interrupt_handlers[num] != 0) {
        isr_t handler = interrupt_handlers[num];
        handler(err);
    } else {
        fault_handler(num, err);
    }
}