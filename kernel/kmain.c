#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "idt.h"
#include "fault_handler.h"
#include "mem.h"
#include "paging.h"
#include "heap.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x0F);

    idt_init();
    keyboard_init();
    timer_init(100);
    mem_init(1024 * 1024);
    paging_init();
    heap_init((void*)0xC0000000, 1024 * 1024);
    terminal_init();

    screen_writeln("All systems ready", 0x0A);
    terminal_run();
}