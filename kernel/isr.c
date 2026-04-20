#include "isr.h"
#include "fault_handler.h"
#include "paging.h"

void isr_handler(unsigned int isr_num, unsigned int err_code) {
    if (isr_num == 14) {
        unsigned int faulting_address;
        asm volatile("mov %%cr2, %0" : "=r"(faulting_address));

        unsigned int present = !(err_code & 0x1);
        unsigned int rw = err_code & 0x2;
        unsigned int us = err_code & 0x4;
        unsigned int reserved = err_code & 0x8;
        unsigned int id = err_code & 0x10;

        fault_handler(isr_num, err_code);
    } else {
        fault_handler(isr_num, err_code);
    }
}