#include "fault_handler.h"
#include "screen.h"
#include "idt.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_set_color(0x0C);
    screen_writeln("EXCEPTION OCCURRED", 0x0C);

    const char *exceptions[] = {
        "Divide by zero",
        "Debug",
        "Non-maskable interrupt",
        "Breakpoint",
        "Overflow",
        "Bound range exceeded",
        "Invalid opcode",
        "Device not available",
        "Double fault",
        "Coprocessor segment overrun",
        "Invalid TSS",
        "Segment not present",
        "Stack segment fault",
        "General protection fault",
        "Page fault",
        "Reserved",
        "x87 floating point exception",
        "Alignment check",
        "Machine check",
        "SIMD floating point exception",
        "Virtualization exception",
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
        screen_writeln(exceptions[num], 0x0C);
    } else {
        screen_writeln("Unknown exception", 0x0C);
    }

    if (err != 0) {
        screen_writeln("Error code:", 0x0C);
    }

    while (1) {
        asm volatile("hlt");
    }
}