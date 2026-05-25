#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "mouse.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    keyboard_init();
    timer_init(100);
    mouse_init();
    terminal_init();

    screen_writeln("Kernel initialized", 0x0A);
    terminal_run();
}