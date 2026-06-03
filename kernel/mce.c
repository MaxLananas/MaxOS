#include "mce.h"
#include "screen.h"

void mce_init(void) {
    screen_writeln("MCE initialized", 0x0F);
}