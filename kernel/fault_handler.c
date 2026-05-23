#include "fault_handler.h"
#include "../drivers/screen.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("EXCEPTION OCCURRED", 0x0C);
    screen_writeln("Exception number:", 0x0C);
    // TODO: Convert num to string and display
    while (1);
}