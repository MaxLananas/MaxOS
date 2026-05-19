#include "isr.h"
#include "idt.h"
#include "io.h"
#include "fault_handler.h"

void isr_handler(unsigned int num, unsigned int err) {
    fault_handler(num, err);
}