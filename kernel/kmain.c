#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "idt.h"
#include "fault_handler.h"
#include "terminal.h"
#include "mouse.h"
#include "paging.h"
#include "mem.h"
#include "heap.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x0F);

    idt_init();
    keyboard_init();
    timer_init(100);
    mouse_init();
    paging_init();
    mem_init(1024 * 1024); // 1MB
    heap_init((void*)0xC0000000, 1024 * 1024); // 1MB heap

    screen_writeln("Initialization complete", 0x0A);
    terminal_init();
    terminal_run();
}