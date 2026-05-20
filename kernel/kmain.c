#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "timer.h"
#include "mouse.h"
#include "mem.h"
#include "paging.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x0A);

    idt_init();
    timer_init(100);
    keyboard_init();
    mouse_init();
    mem_init(1024 * 1024);
    paging_init();

    terminal_init();
    terminal_run();

    for (;;);
}