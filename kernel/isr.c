#include "isr.h"
#include "fault_handler.h"

void isr_handler(unsigned int isr_num, unsigned int err_code) {
    fault_handler(isr_num, err_code);
}