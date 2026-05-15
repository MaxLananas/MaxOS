#include "fault_handler.h"
#include "screen.h"
#include "idt.h"

void fault_handler(registers_t regs) {
    screen_set_color(0x0C);
    screen_writeln("EXCEPTION: ", 0x0C);
    screen_putchar('0' + regs.int_no, 0x0C);
    screen_writeln(" (", 0x0C);
    screen_writeln("EIP: ", 0x0C);
    screen_putchar('0' + (regs.eip >> 24), 0x0C);
    screen_putchar('0' + ((regs.eip >> 16) & 0xFF), 0x0C);
    screen_putchar('0' + ((regs.eip >> 8) & 0xFF), 0x0C);
    screen_putchar('0' + (regs.eip & 0xFF), 0x0C);
    screen_writeln(")", 0x0C);
    for (;;);
}