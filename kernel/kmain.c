#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "mouse.h"
#include "terminal.h"
#include "idt.h"
#include "fault_handler.h"

void kmain(void) {
    screen_init();
    screen_clear();
    keyboard_init();
    timer_init(100);
    mouse_init();
    idt_init();
    terminal_init();

    screen_writeln("Kernel initialized", 0x0A);
    terminal_run();
}