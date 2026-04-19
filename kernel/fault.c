#include "idt.h"
#include "io.h"
#include "exceptions.h"

void fault_handler(unsigned int *esp) {
    unsigned int eip = esp[14];
    unsigned int cs = esp[13];
    unsigned int eflags = esp[12];
    unsigned int esp_val = esp[11];
    unsigned int ss = esp[10];

    outb(0x3F8, 'F');
    outb(0x3F8, 'A');
    outb(0x3F8, 'U');
    outb(0x3F8, 'L');
    outb(0x3F8, 'T');

    while(1);
}