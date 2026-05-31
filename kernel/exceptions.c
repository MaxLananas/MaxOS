#include "exceptions.h"
#include "fault_handler.h"
#include "screen.h"

void exceptions_init(void)
{
    screen_writeln("Exceptions initialized", 0x0A);
}