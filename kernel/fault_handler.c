#include "idt.h"

void fault_handler(unsigned int *esp) {
    unsigned int isr_num = esp[11];
    while(1);
}