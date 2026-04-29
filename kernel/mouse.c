#include "io.h"
#include "mouse.h"
#include "screen.h"

void mouse_init(void) {
}

void mouse_handler(void) {
    screen_putchar('M', 0x0F);
}