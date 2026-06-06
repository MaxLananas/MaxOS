#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "timer.h"
#include "mouse.h"
#include "terminal.h"
#include "mem.h"
#include "heap.h"
#include "paging.h"

void kmain(void) {
    screen_init();
    idt_init();
    keyboard_init();
    timer_init(100);
    mouse_init();
    paging_init();
    heap_init((void*)0xC0000000, 0x100000);
    mem_init(1024 * 1024);
    terminal_init();

    screen_writeln("Kernel initialized", 0x0F);
    terminal_run();
}