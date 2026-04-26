#include "screen.h"
#include "keyboard.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x0A);
    keyboard_init();
    terminal_init();
    terminal_run();
}