#include "screen.h"
#include "keyboard.h"
#include "terminal.h"
#include "mouse.h"

void kmain(void) {
    screen_init();
    keyboard_init();
    terminal_init();
    mouse_init();
    terminal_run();
}