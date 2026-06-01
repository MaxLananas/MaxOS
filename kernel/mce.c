#include "mce.h"
#include "screen.h"

void mce_init(void) {
    screen_writeln("Machine check exception initialized", 0x0F);
}