#include "../drivers/screen.h"
#include "../kernel/fault_handler.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_clear();
    screen_set_color(0x0C);
    screen_writeln("*** FAULT ***", 0x0C);
    screen_set_color(0x0F);
    screen_write("Fault: ", 0x0F);
    screen_write_hex(num);
    screen_write(" Error: ", 0x0F);
    screen_write_hex(err);
    screen_writeln("", 0x0F);

    for (;;) {
        __asm__ volatile ("hlt");
    }
}