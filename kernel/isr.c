#include "isr.h"
#include "idt.h"
#include "fault_handler.h"
#include "io.h"

void isr_handler(unsigned int num, unsigned int err) {
    if (num < 32) {
        fault_handler(num, err);
    }
}