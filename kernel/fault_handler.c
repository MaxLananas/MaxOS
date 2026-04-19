#include "io.h"

void fault_handler(unsigned int isr_num, unsigned int esp) {
    outb(0x20, 0x20);
    if (isr_num >= 40) outb(0xA0, 0x20);
}