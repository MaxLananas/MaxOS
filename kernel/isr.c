#include "isr.h"
#include "fault_handler.h"

void isr_handler(unsigned int num, unsigned int err) {
    fault_handler((registers_t){
        .int_no = num,
        .err_code = err
    });
}