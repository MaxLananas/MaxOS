#include "screen.h"
#include "keyboard.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    keyboard_init();
    terminal_init();
    terminal_run();
}