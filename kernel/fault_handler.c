#include "fault_handler.h"
#include "screen.h"
#include "idt.h"

void fault_handler(registers_t regs) {
    screen_set_color(0x0C);
    screen_writeln("EXCEPTION: ", 0x0C);
    switch(regs.int_no) {
        case 0:  screen_writeln("Divide by zero", 0x0C); break;
        case 1:  screen_writeln("Debug", 0x0C); break;
        case 2:  screen_writeln("Non-maskable interrupt", 0x0C); break;
        case 3:  screen_writeln("Breakpoint", 0x0C); break;
        case 4:  screen_writeln("Overflow", 0x0C); break;
        case 5:  screen_writeln("Bound range exceeded", 0x0C); break;
        case 6:  screen_writeln("Invalid opcode", 0x0C); break;
        case 7:  screen_writeln("Device not available", 0x0C); break;
        case 8:  screen_writeln("Double fault", 0x0C); break;
        case 10: screen_writeln("Invalid TSS", 0x0C); break;
        case 11: screen_writeln("Segment not present", 0x0C); break;
        case 12: screen_writeln("Stack segment fault", 0x0C); break;
        case 13: screen_writeln("General protection fault", 0x0C); break;
        case 14: screen_writeln("Page fault", 0x0C); break;
        case 16: screen_writeln("FPU error", 0x0C); break;
        case 17: screen_writeln("Alignment check", 0x0C); break;
        case 18: screen_writeln("Machine check", 0x0C); break;
        case 19: screen_writeln("SIMD FPU exception", 0x0C); break;
        default: screen_writeln("Unknown exception", 0x0C); break;
    }
    screen_writeln("System halted!", 0x0C);
    for(;;);
}