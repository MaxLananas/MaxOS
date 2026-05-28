#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "timer.h"
#include "mouse.h"
#include "mem.h"
#include "paging.h"
#include "heap.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    idt_init();
    keyboard_init();
    timer_init(100);
    mouse_init();
    mem_init(1024 * 1024);
    paging_init();
    heap_init((void*)0xC0000000, 1024 * 1024);
    terminal_init();

    screen_writeln("Kernel initialized", 0x0A);
    terminal_run();
}