#include "kernel/kmain.h"
#include "drivers/screen.h"

void kmain(void) {
    screen_init();
    screen_set_color(0x0F);
    screen_writeln("Kernel started successfully", 0x0A);
}