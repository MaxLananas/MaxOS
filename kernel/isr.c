#include "kernel/idt.h"
#include "kernel/io.h"
#include "kernel/fault_handler.h"

void isr_handler(unsigned int num, unsigned int err) {
    if (num < 32) {
        fault_handler(num, err);
    }
}