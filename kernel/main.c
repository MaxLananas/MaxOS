#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "timer.h"
#include "fault_handler.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    idt_init();
    keyboard_init();
    timer_init(100);
    terminal_init();

    screen_writeln("Kernel initialized", 0x0A);
    terminal_run();

    for (;;);
}