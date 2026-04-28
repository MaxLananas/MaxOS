#include "kernel/fault_handler.h"
#include "kernel/screen.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("Page fault", 0x0F);
}