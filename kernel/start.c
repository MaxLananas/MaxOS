#include "screen.h"
#include "idt.h"
#include "isr.h"
#include "timer.h"
#include "keyboard.h"
#include "mouse.h"
#include "mem.h"
#include "heap.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x0F);

    idt_init();
    keyboard_init();
    mouse_init();
    timer_init(100);

    screen_writeln("Initialization complete", 0x0A);
    terminal_init();
    terminal_run();
}