#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "irq.h"
#include "timer.h"
#include "fault_handler.h"
#include "terminal.h"
#include "mouse.h"
#include "paging.h"
#include "mem.h"
#include "heap.h"

void kmain(void) {
    screen_init();
    screen_clear();

    idt_init();
    irq_init();
    timer_init(100);
    keyboard_init();
    mouse_init();
    paging_init();
    mem_init(1024 * 1024); // 1MB
    heap_init((void*)0xC0000000, 1024 * 1024); // 1MB heap

    screen_writeln("Kernel initialized", 0x0A);
    terminal_init();
    terminal_run();
}