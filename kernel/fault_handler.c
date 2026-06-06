#include "fault_handler.h"
#include "screen.h"
#include "idt.h"

void fault_handler(unsigned int num, unsigned int err)
{
    screen_set_color(0x0C);
    screen_writeln("Exception occurred!", 0x0C);

    switch (num) {
        case 0:
            screen_writeln("Divide by zero", 0x0C);
            break;
        case 1:
            screen_writeln("Debug", 0x0C);
            break;
        case 2:
            screen_writeln("NMI", 0x0C);
            break;
        case 3:
            screen_writeln("Breakpoint", 0x0C);
            break;
        case 4:
            screen_writeln("Overflow", 0x0C);
            break;
        case 5:
            screen_writeln("Bound range", 0x0C);
            break;
        case 6:
            screen_writeln("Invalid opcode", 0x0C);
            break;
        case 7:
            screen_writeln("Device not available", 0x0C);
            break;
        case 8:
            screen_writeln("Double fault", 0x0C);
            break;
        case 9:
            screen_writeln("Coprocessor segment overrun", 0x0C);
            break;
        case 10:
            screen_writeln("Invalid TSS", 0x0C);
            break;
        case 11:
            screen_writeln("Segment not present", 0x0C);
            break;
        case 12:
            screen_writeln("Stack segment fault", 0x0C);
            break;
        case 13:
            screen_writeln("General protection fault", 0x0C);
            break;
        case 14:
            screen_writeln("Page fault", 0x0C);
            break;
        case 16:
            screen_writeln("x87 FPU error", 0x0C);
            break;
        case 17:
            screen_writeln("Alignment check", 0x0C);
            break;
        case 18:
            screen_writeln("Machine check", 0x0C);
            break;
        case 19:
            screen_writeln("SIMD FPU exception", 0x0C);
            break;
        default:
            screen_writeln("Unknown exception", 0x0C);
            break;
    }

    if (err != 0) {
        screen_writeln("Error code:", 0x0C);
    }

    asm volatile("cli");
    asm volatile("hlt");
}