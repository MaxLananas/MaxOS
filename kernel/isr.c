#include "isr.h"
#include "idt.h"
#include "screen.h"
#include "io.h"
#include "irq.h"
#include "fault_handler.h"

void isr_handler(unsigned int num, unsigned int err) {
    if (num < 32) {
        fault_handler(num, err);
    } else {
        irq_handler(num - 32);
    }
}