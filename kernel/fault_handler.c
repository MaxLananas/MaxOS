#include "fault_handler.h"
#include "screen.h"
#include "io.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_set_color(0x0C);
    screen_clear();
    screen_writeln("EXCEPTION OCCURRED!", 0x0F);
    screen_writeln("System Halted", 0x0F);

    switch(num) {
        case 0: screen_writeln("Divide by Zero", 0x0F); break;
        case 1: screen_writeln("Debug", 0x0F); break;
        case 2: screen_writeln("NMI", 0x0F); break;
        case 3: screen_writeln("Breakpoint", 0x0F); break;
        case 4: screen_writeln("Overflow", 0x0F); break;
        case 5: screen_writeln("Bound Range", 0x0F); break;
        case 6: screen_writeln("Invalid Opcode", 0x0F); break;
        case 7: screen_writeln("Device Not Available", 0x0F); break;
        case 8: screen_writeln("Double Fault", 0x0F); break;
        case 9: screen_writeln("Coprocessor Segment Overrun", 0x0F); break;
        case 10: screen_writeln("Invalid TSS", 0x0F); break;
        case 11: screen_writeln("Segment Not Present", 0x0F); break;
        case 12: screen_writeln("Stack Segment Fault", 0x0F); break;
        case 13: screen_writeln("General Protection Fault", 0x0F); break;
        case 14: screen_writeln("Page Fault", 0x0F); break;
        case 16: screen_writeln("Floating Point", 0x0F); break;
        case 17: screen_writeln("Alignment Check", 0x0F); break;
        case 18: screen_writeln("Machine Check", 0x0F); break;
        case 19: screen_writeln("SIMD Floating Point", 0x0F); break;
        default: screen_writeln("Unknown Exception", 0x0F); break;
    }

    if(err != 0) {
        screen_writeln("Error code: ", 0x0F);
        screen_putchar('0' + err, 0x0F);
    }

    for(;;);
}