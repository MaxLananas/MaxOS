#include "fault_handler.h"
#include "screen.h"
#include "idt.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_clear();
    screen_writeln("Exception occurred!", 0x0C);
    screen_writeln("System halted.", 0x0C);
    while (1) {
        __asm__ __volatile__("hlt");
    }
}