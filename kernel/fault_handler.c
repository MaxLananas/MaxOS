#include "fault_handler.h"
#include "exceptions.h"
#include "io.h"

void fault_handler(unsigned int isr_num, unsigned int err_code) {
    outb(0x20,0x20);
    outb(0xA0,0x20);

    switch(isr_num) {
        case 0: outb(0x3F8,'D'); break;
        case 1: outb(0x3F8,'D'); break;
        case 2: outb(0x3F8,'N'); break;
        case 3: outb(0x3F8,'B'); break;
        case 4: outb(0x3F8,'O'); break;
        case 5: outb(0x3F8,'B'); break;
        case 6: outb(0x3F8,'U'); break;
        case 7: outb(0x3F8,'N'); break;
        case 8: double_fault_handler(err_code); break;
        case 10: general_protection_fault_handler(err_code); break;
        case 11: outb(0x3F8,'S'); break;
        case 12: outb(0x3F8,'S'); break;
        case 13: general_protection_fault_handler(err_code); break;
        case 14: page_fault_handler(err_code,err_code); break;
        case 16: outb(0x3F8,'X'); break;
        case 17: outb(0x3F8,'A'); break;
        case 18: machine_check_handler(); break;
        case 19: outb(0x3F8,'S'); break;
        default: outb(0x3F8,'?'); break;
    }
}