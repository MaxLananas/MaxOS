#include "kernel/fault_handler.h"
#include "drivers/screen.h"

void fault_handler(unsigned int num, unsigned int err) {
    char *exception_messages[] = {
        "Division By Zero",
        "Debug",
        "Non Maskable Interrupt",
        "Breakpoint",
        "Into Detected Overflow",
        "Out of Bounds",
        "Invalid Opcode",
        "No Coprocessor",
        "Double Fault",
        "Coprocessor Segment Overrun",
        "Bad TSS",
        "Segment Not Present",
        "Stack Fault",
        "General Protection Fault",
        "Page Fault",
        "Unknown Interrupt",
        "Coprocessor Fault",
        "Alignment Check",
        "Machine Check",
        "Reserved",
        "Reserved",
        "Reserved",
        "Reserved",
        "Reserved",
        "Reserved",
        "Reserved",
        "Reserved",
        "Reserved",
        "Reserved",
        "Reserved",
        "Reserved"
    };

    screen_writeln("EXCEPTION: ", 0x0C);
    screen_writeln(exception_messages[num], 0x0C);
    screen_writeln("Error code: ", 0x0C);
    screen_writeln("System halted", 0x0C);
    for(;;);
}