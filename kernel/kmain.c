#include "kmain.h"
#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "timer.h"
#include "fault_handler.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x0A);

    idt_init();
    fault_handler_init();
    keyboard_init();
    timer_init(100);

    screen_writeln("Initialization complete", 0x0A);
    terminal_init();
    terminal_run();
}