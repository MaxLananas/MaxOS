#include "fault_handler.h"
#include "screen.h"
#include "io.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_clear();
    screen_writeln("EXCEPTION OCCURRED", 0x0C);
    screen_writeln("", 0x0C);

    static const char *exception_messages[] = {
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

    if (num < 32) {
        screen_writeln(exception_messages[num], 0x0C);
    } else {
        screen_writeln("Unknown Exception", 0x0C);
    }

    screen_writeln("", 0x0C);
    screen_writeln("System Halted", 0x0C);
    while (1) {
        asm volatile("hlt");
    }
}