#include "isr.h"
#include "screen.h"

void isr_handler(unsigned int num, unsigned int err) {
    screen_writeln("Received interrupt", 0x0F);
}