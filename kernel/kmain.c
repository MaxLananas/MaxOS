#include "screen.h"
#include "keyboard.h"
#include "terminal.h"
#include "mouse.h"
#include "idt.h"
#include "timer.h"
#include "memory.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x0F);

    idt_init();
    keyboard_init();
    mouse_init();
    timer_init(100);
    mem_init(1024 * 1024);

    terminal_init();
    terminal_run();
}