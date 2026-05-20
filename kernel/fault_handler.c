#include "fault_handler.h"
#include "screen.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("CPU EXCEPTION:", 0x0C);
    screen_writeln("Number: ", 0x0C);
    screen_write_hex(num);
    screen_writeln("", 0x0C);
    screen_writeln("Error: ", 0x0C);
    screen_write_hex(err);
    screen_writeln("", 0x0C);

    while (1) {
        __asm__ volatile("cli; hlt");
    }
}