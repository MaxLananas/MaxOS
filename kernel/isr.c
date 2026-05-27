#include "isr.h"
#include "idt.h"
#include "screen.h"
#include "io.h"
#include "irq.h"
#include "fault_handler.h"
#include "mce.h"
#include "nmi.h"

void isr_handler(unsigned int num, unsigned int err) {
    if (num < 32) {
        switch (num) {
            case 0: screen_writeln("Divide by zero", 0x0C); break;
            case 1: screen_writeln("Debug", 0x0C); break;
            case 2: screen_writeln("NMI", 0x0C); break;
            case 3: screen_writeln("Breakpoint", 0x0C); break;
            case 4: screen_writeln("Overflow", 0x0C); break;
            case 5: screen_writeln("Bound range", 0x0C); break;
            case 6: screen_writeln("Invalid opcode", 0x0C); break;
            case 7: screen_writeln("Device not available", 0x0C); break;
            case 8: screen_writeln("Double fault", 0x0C); break;
            case 9: screen_writeln("Coprocessor segment overrun", 0x0C); break;
            case 10: screen_writeln("Invalid TSS", 0x0C); break;
            case 11: screen_writeln("Segment not present", 0x0C); break;
            case 12: screen_writeln("Stack segment fault", 0x0C); break;
            case 13: screen_writeln("General protection fault", 0x0C); break;
            case 14: screen_writeln("Page fault", 0x0C); break;
            case 16: screen_writeln("FPU error", 0x0C); break;
            case 17: screen_writeln("Alignment check", 0x0C); break;
            case 18: screen_writeln("Machine check", 0x0C); mce_handler(num, err); break;
            case 19: screen_writeln("SIMD FPU", 0x0C); break;
            default: screen_writeln("Reserved", 0x0C); break;
        }
        fault_handler(num, err);
    } else {
        irq_handler(num);
    }
}