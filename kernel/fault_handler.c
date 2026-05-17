#include "fault_handler.h"
#include "screen.h"

void fault_handler(registers_t regs) {
    screen_set_color(0x0C);
    screen_writeln("Exception occurred!", 0x0C);
    screen_write("Interrupt: ", 0x0C);
    screen_putchar('0' + regs.int_no / 10, 0x0C);
    screen_putchar('0' + regs.int_no % 10, 0x0C);
    screen_putchar('\n', 0x0C);
    screen_write("Error code: ", 0x0C);
    screen_putchar('0' + regs.err_code / 10, 0x0C);
    screen_putchar('0' + regs.err_code % 10, 0x0C);
    screen_putchar('\n', 0x0C);
    screen_write("EIP: ", 0x0C);
    screen_putchar('0' + (regs.eip >> 24) & 0xFF, 0x0C);
    screen_putchar('0' + (regs.eip >> 16) & 0xFF, 0x0C);
    screen_putchar('0' + (regs.eip >> 8) & 0xFF, 0x0C);
    screen_putchar('0' + regs.eip & 0xFF, 0x0C);
    screen_putchar('\n', 0x0C);

    while(1);
}