#include "fault_handler.h"
#include "screen.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("Exception occurred!", 0x0C);
    while (1) {
        __asm__ volatile("hlt");
    }
}