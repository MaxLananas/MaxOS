#include "mouse.h"
#include "screen.h"

void mouse_init(void) {
    screen_writeln("Mouse initialized", 0x0F);
}

void mouse_handler(void) {
    screen_writeln("Mouse event", 0x0F);
}