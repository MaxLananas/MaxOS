#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "fault_handler.h"
#include "terminal.h"
#include "mouse.h"

void kmain(void) {
    screen_init();
    keyboard_init();
    timer_init(100);
    mouse_init();
    terminal_init();
    terminal_run();
}