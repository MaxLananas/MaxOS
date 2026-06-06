#include "exceptions.h"
#include "screen.h"
#include "fault_handler.h"

void exceptions_init(void) {
    screen_writeln("Exceptions initialized", 0x0C);
}