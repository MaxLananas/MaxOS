#include "mouse.h"
#include "../kernel/io.h"
#include "../kernel/screen.h"

void mouse_init(void) {
    // Implementation
}

void mouse_handler(void) {
    // Implementation
    screen_putchar('M', 0x0F);
}