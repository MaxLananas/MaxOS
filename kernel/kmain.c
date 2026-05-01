#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "irq.h"
#include "timer.h"
#include "mouse.h"

void kmain(void) {
    screen_init();
    idt_init();
    irq_init();
    keyboard_init();
    timer_init(100);
    mouse_init();

    screen_writeln("Kernel initialized", 0x0A);
    screen_writeln("Type commands below:", 0x0F);

    terminal_init();
    terminal_run();
}