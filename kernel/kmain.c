#include "screen.h"
#include "keyboard.h"
#include "terminal.h"
#include "idt.h"
#include "timer.h"
#include "mouse.h"

void kmain(void) {
    screen_init();
    screen_clear();

    idt_init();
    keyboard_init();
    timer_init(100);
    mouse_init();

    screen_writeln("Kernel initialized", 0x0A);
    terminal_init();
    terminal_run();
}