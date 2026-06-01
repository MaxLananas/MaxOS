#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "irq.h"
#include "timer.h"
#include "fault_handler.h"
#include "mouse.h"
#include "mem.h"
#include "paging.h"
#include "heap.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_set_color(0x0A);
    screen_writeln("Kernel started", 0x0A);

    idt_init();
    irq_init();
    keyboard_init();
    timer_init(100);
    mouse_init();
    mem_init(1024 * 1024);
    heap_init((void*)0xC0000000, 1024 * 1024);
    paging_init();
    terminal_init();

    screen_writeln("All systems initialized", 0x0A);
    terminal_run();
}