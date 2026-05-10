#include "screen.h"
#include "keyboard.h"
#include "terminal.h"
#include "idt.h"
#include "timer.h"
#include "mouse.h"
#include "fault_handler.h"
#include "paging.h"
#include "mem.h"
#include "heap.h"

void kmain(void) {
    screen_init();
    idt_init();
    keyboard_init();
    timer_init(100);
    mouse_init();
    paging_init();
    mem_init(1024 * 1024);
    heap_init((void*)0xC0000000, 1024 * 1024);
    terminal_init();
    terminal_run();
}