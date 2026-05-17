#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    keyboard_init();
    timer_init(100);
    terminal_init();
    terminal_run();
}