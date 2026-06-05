#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "mouse.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x0F);
    keyboard_init();
    timer_init(100);
    mouse_init();
    terminal_init();
    terminal_run();
}