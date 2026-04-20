#include "fault_handler.h"
#include "screen.h"
#include "paging.h"

void fault_handler(unsigned int isr_num, unsigned int err_code) {
    screen_write("Interrupt received: ");
    screen_write_hex(isr_num);
    screen_write("\n");

    if (isr_num == 14) {
        unsigned int faulting_address;
        asm volatile("mov %%cr2, %0" : "=r"(faulting_address));

        screen_write("Page fault at address: ");
        screen_write_hex(faulting_address);
        screen_write("\n");

        unsigned int present = !(err_code & 0x1);
        unsigned int rw = err_code & 0x2;
        unsigned int us = err_code & 0x4;
        unsigned int reserved = err_code & 0x8;
        unsigned int id = err_code & 0x10;

        if (present) {
            screen_write("Page not present\n");
        }
        if (rw) {
            screen_write("Attempted write\n");
        }
        if (us) {
            screen_write("User mode\n");
        }
        if (reserved) {
            screen_write("Reserved bits overwritten\n");
        }
        if (id) {
            screen_write("Instruction fetch\n");
        }
    }

    asm volatile("hlt");
}