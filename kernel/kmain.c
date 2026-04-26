#include "screen.h"
#include "keyboard.h"
#include "terminal.h"
#include "idt.h"
#include "timer.h"
#include "memory.h"
#include "paging.h"
#include "fault_handler.h"

void kmain(void) {
    screen_init();
    screen_clear();
    idt_init();
    keyboard_init();
    timer_init(100);
    paging_init();
    mem_init(1024 * 1024);
    heap_init((void*)0xC0000000, 0x100000);
    terminal_init();
    terminal_run();
}