#include "screen.h"
#include "keyboard.h"
#include "terminal.h"
#include "idt.h"
#include "timer.h"
#include "mouse.h"
#include "fault_handler.h"

void kmain(void) {
    screen_init();
    screen_clear();

    idt_init();
    keyboard_init();
    timer_init(100);
    mouse_init();

    terminal_init();
    terminal_run();
}