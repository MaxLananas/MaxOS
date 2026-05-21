#include "fault_handler.h"
#include "screen.h"
#include "io.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("EXCEPTION OCCURRED", 0x0C);
    screen_writeln("System Halted", 0x0C);
    for (;;) {
        asm volatile("hlt");
    }
}