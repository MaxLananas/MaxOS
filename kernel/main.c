#include "drivers/screen.h"
#include "kernel/keyboard.h"
#include "kernel/timer.h"
#include "kernel/idt.h"
#include "kernel/fault_handler.h"
#include "kernel/mouse.h"

void kmain(void) {
    screen_init();
    idt_init();
    keyboard_init();
    timer_init(100);
    mouse_init();

    screen_writeln("Kernel initialized", 0x0A);
    screen_writeln("Type commands below:", 0x0F);

    terminal_init();
    terminal_run();
}