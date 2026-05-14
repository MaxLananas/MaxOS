#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "terminal.h"
#include "idt.h"
#include "irq.h"

void kmain(void) {
    screen_init();
    idt_init();
    irq_init();
    keyboard_init();
    timer_init(100);
    terminal_init();

    screen_writeln("Kernel initialized", 0x0A);
    terminal_run();
}