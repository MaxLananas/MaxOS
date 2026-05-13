#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "fault_handler.h"
#include "terminal.h"

void kmain(void)
{
    screen_init();
    keyboard_init();
    timer_init(100);
    fault_handler_init();
    terminal_init();
    terminal_run();
}