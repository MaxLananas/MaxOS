#include "isr.h"
#include "fault_handler.h"
#include "screen.h"

extern void *isr_routines[];

void isr_handler(unsigned int num, unsigned int err) {
    fault_handler(num, err);
}