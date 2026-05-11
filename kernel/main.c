#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "fault_handler.h"
#include "idt.h"

void kmain(void) {
    screen_init();
    idt_init();
    keyboard_init();
    timer_init(100);
    fault_handler_init();

    screen_writeln("Kernel initialized", 0x0A);
    screen_writeln("Type commands below:", 0x0F);

    terminal_init();
    terminal_run();
}