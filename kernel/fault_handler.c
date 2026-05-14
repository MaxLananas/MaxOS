#include "fault_handler.h"
#include "screen.h"
#include "io.h"

void fault_handler(registers_t regs) {
    screen_writeln("System fault!", 0x0C);
    screen_writeln("Exception number:", 0x0C);
    screen_putchar('0' + regs.int_no, 0x0C);
    screen_putchar('\n', 0x0C);

    if (regs.err_code != 0) {
        screen_writeln("Error code:", 0x0C);
        screen_putchar('0' + regs.err_code, 0x0C);
        screen_putchar('\n', 0x0C);
    }

    while (1) {
        __asm__ volatile("hlt");
    }
}