#include "fault_handler.h"
#include "screen.h"
#include "io.h"

void fault_handler(registers_t regs) {
    screen_set_color(0x0C);
    screen_writeln("EXCEPTION: ", 0x0C);
    screen_putchar('0' + regs.int_no, 0x0C);
    screen_writeln(" (", 0x0C);
    screen_putchar('0' + (regs.err_code >> 4), 0x0C);
    screen_putchar('0' + (regs.err_code & 0xF), 0x0C);
    screen_writeln(")", 0x0C);
    screen_writeln("EAX:", 0x0C);
    screen_putchar('0' + (regs.eax >> 4), 0x0C);
    screen_putchar('0' + (regs.eax & 0xF), 0x0C);
    screen_putchar(' ', 0x0C);
    screen_writeln("EBX:", 0x0C);
    screen_putchar('0' + (regs.ebx >> 4), 0x0C);
    screen_putchar('0' + (regs.ebx & 0xF), 0x0C);
    screen_putchar(' ', 0x0C);
    screen_writeln("ECX:", 0x0C);
    screen_putchar('0' + (regs.ecx >> 4), 0x0C);
    screen_putchar('0' + (regs.ecx & 0xF), 0x0C);
    screen_putchar(' ', 0x0C);
    screen_writeln("EDX:", 0x0C);
    screen_putchar('0' + (regs.edx >> 4), 0x0C);
    screen_putchar('0' + (regs.edx & 0xF), 0x0C);
    screen_putchar(' ', 0x0C);
    screen_writeln("EIP:", 0x0C);
    screen_putchar('0' + (regs.eip >> 4), 0x0C);
    screen_putchar('0' + (regs.eip & 0xF), 0x0C);
    for(;;);
}