#include "fault_handler.h"
#include "screen.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("Exception: ", 0x04);
    switch(num) {
        case 0: screen_writeln("Divide by zero", 0x04); break;
        case 1: screen_writeln("Debug", 0x04); break;
        case 2: screen_writeln("NMI", 0x04); break;
        case 3: screen_writeln("Breakpoint", 0x04); break;
        case 4: screen_writeln("Overflow", 0x04); break;
        case 5: screen_writeln("Bound range", 0x04); break;
        case 6: screen_writeln("Invalid opcode", 0x04); break;
        case 7: screen_writeln("Device not available", 0x04); break;
        case 8: screen_writeln("Double fault", 0x04); break;
        case 9: screen_writeln("Coprocessor segment overrun", 0x04); break;
        case 10: screen_writeln("Invalid TSS", 0x04); break;
        case 11: screen_writeln("Segment not present", 0x04); break;
        case 12: screen_writeln("Stack segment fault", 0x04); break;
        case 13: screen_writeln("General protection fault", 0x04); break;
        case 14: screen_putchar('P', 0x04); screen_writeln("age fault", 0x04); break;
        case 15: screen_writeln("Reserved", 0x04); break;
        case 16: screen_writeln("x87 FPU error", 0x04); break;
        case 17: screen_writeln("Alignment check", 0x04); break;
        case 18: screen_writeln("Machine check", 0x04); break;
        case 19: screen_writeln("SIMD FPU exception", 0x04); break;
        case 20: screen_writeln("Virtualization exception", 0x04); break;
        case 21: screen_writeln("Control protection exception", 0x04); break;
        default: screen_writeln("Unknown exception", 0x04); break;
    }

    if (num == 14) {
        unsigned int cr2;
        __asm__ volatile("mov %%cr2, %0" : "=r"(cr2));
        screen_writeln("Address: 0x", 0x04);
        screen_putchar("0123456789ABCDEF"[(cr2 >> 28) & 0xF], 0x04);
        screen_putchar("0123456789ABCDEF"[(cr2 >> 24) & 0xF], 0x04);
        screen_putchar("0123456789ABCDEF"[(cr2 >> 20) & 0xF], 0x04);
        screen_putchar("0123456789ABCDEF"[(cr2 >> 16) & 0xF], 0x04);
        screen_putchar("0123456789ABCDEF"[(cr2 >> 12) & 0xF], 0x04);
        screen_putchar("0123456789ABCDEF"[(cr2 >> 8) & 0xF], 0x04);
        screen_putchar("0123456789ABCDEF"[(cr2 >> 4) & 0xF], 0x04);
        screen_putchar("0123456789ABCDEF"[cr2 & 0xF], 0x04);
        screen_putchar('\n', 0x04);
    }

    while(1);
}