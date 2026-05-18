#include "fault_handler.h"
#include "screen.h"
#include "idt.h"

void fault_handler(registers_t regs) {
    screen_writeln("Exception: ", 0x0F);
    switch(regs.int_no) {
        case 0:  screen_writeln("Division By Zero", 0x0F); break;
        case 1:  screen_writeln("Debug", 0x0F); break;
        case 2:  screen_writeln("Non Maskable Interrupt", 0x0F); break;
        case 3:  screen_writeln("Breakpoint", 0x0F); break;
        case 4:  screen_writeln("Into Detected Overflow", 0x0F); break;
        case 5:  screen_writeln("Out of Bounds", 0x0F); break;
        case 6:  screen_writeln("Invalid Opcode", 0x0F); break;
        case 7:  screen_writeln("No Coprocessor", 0x0F); break;
        case 8:  screen_writeln("Double Fault", 0x0F); break;
        case 9:  screen_writeln("Coprocessor Segment Overrun", 0x0F); break;
        case 10: screen_writeln("Bad TSS", 0x0F); break;
        case 11: screen_writeln("Segment Not Present", 0x0F); break;
        case 12: screen_writeln("Stack Fault", 0x0F); break;
        case 13: screen_writeln("General Protection Fault", 0x0F); break;
        case 14: screen_writeln("Page Fault", 0x0F); break;
        case 15: screen_writeln("Unknown Interrupt", 0x0F); break;
        case 16: screen_writeln("Coprocessor Fault", 0x0F); break;
        case 17: screen_writeln("Alignment Check", 0x0F); break;
        case 18: screen_writeln("Machine Check", 0x0F); break;
        default: screen_writeln("Unknown Exception", 0x0F); break;
    }
    screen_writeln("Error code: ", 0x0F);
    screen_putchar('0' + regs.err_code / 10, 0x0F);
    screen_putchar('0' + regs.err_code % 10, 0x0F);
    for(;;);
}
```=== END FILE ===