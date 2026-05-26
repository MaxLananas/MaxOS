#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "idt.h"
#include "fault_handler.h"
#include "mouse.h"
#include "mem.h"
#include "paging.h"
#include "heap.h"

void kmain(void) {
    screen_init();
    idt_init();
    keyboard_init();
    timer_init(100);
    mouse_init();
    mem_init(1024 * 1024);
    paging_init();
    heap_init((void *)0xC0000000, 1024 * 1024);

    screen_writeln("Kernel initialized", 0x0A);
    screen_writeln("Type 'help' for commands", 0x0F);

    terminal_init();
    terminal_run();
}