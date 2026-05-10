#include "kmain.h"
#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "idt.h"
#include "fault_handler.h"
#include "mouse.h"
#include "paging.h"
#include "mem.h"
#include "heap.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    idt_init();
    keyboard_init();
    timer_init(100);
    mouse_init();
    paging_init();
    mem_init(1024);
    heap_init((void *)0x200000, 0x100000);
    terminal_init();
    terminal_run();
}