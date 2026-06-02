#include "exceptions.h"
#include "fault_handler.h"
#include "screen.h"

void exceptions_init(void) {
    screen_writeln("Exceptions initialized", 0x0F);
}

void exception_handler(unsigned int num, unsigned int err) {
    fault_handler(num, err);
}