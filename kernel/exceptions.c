#include "exceptions.h"
#include "fault_handler.h"
#include "../screen.h"

void exceptions_init(void) {
    screen_writeln("EXCEPTIONS: Initialized", 0x02);
}