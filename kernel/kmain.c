#include "kmain.h"
#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "timer.h"
#include "exceptions.h"

void kmain(void) {
    screen_init();
    idt_init();
    exceptions_init();
    timer_init(100);
    keyboard_init();

    screen_writeln("Kernel initialized successfully", 0x0A);
    screen_writeln("Type commands below:", 0x0A);

    terminal_init();
    terminal_run();
}