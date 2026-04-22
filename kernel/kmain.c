#include "kernel/screen.h"
#include "kernel/keyboard.h"
#include "kernel/idt.h"
#include "kernel/timer.h"
#include "kernel/memory.h"

void kmain(void) {
    screen_init();
    idt_init();
    keyboard_init();
    timer_init(100);
    mem_init(1024 * 1024);

    screen_writeln("Kernel started successfully", 0x0A);
    screen_writeln("Type 'help' for commands", 0x0F);

    terminal_init();
    terminal_run();
}