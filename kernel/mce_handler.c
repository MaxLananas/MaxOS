#include "mce_handler.h"
#include "screen.h"

void mce_handler_init(void) {
    screen_writeln("MCE handler initialized", 0x0F);
}