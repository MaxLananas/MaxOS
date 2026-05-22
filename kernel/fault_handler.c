#include "fault_handler.h"
#include "screen.h"
#include "idt.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_set_color(0x0C);
    screen_writeln("CPU Exception:", 0x0C);
    screen_putchar(' ', 0x0C);

    static const char *exception_messages[] = {
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
        "Security exception",
        "Reserved"
    };

    if (num < 32) {
        screen_write((const char*)exception_messages[num], 0x0C);
    } else {
        screen_write("Unknown exception", 0x0C);
    }

    screen_writeln("", 0x0C);
    screen_writeln("System halted", 0x0C);
    for (;;);
}