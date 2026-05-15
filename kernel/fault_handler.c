#include "drivers/screen.h"
#include "kernel/fault_handler.h"

void fault_handler(registers_t regs) {
    screen_writeln("EXCEPTION OCCURRED", 0x0C);
    screen_writeln("Exception number:", 0x0C);
    screen_putchar('0' + regs.int_no, 0x0C);
    screen_putchar('\n', 0x0C);

    while (1) {
        asm volatile("hlt");
    }
}