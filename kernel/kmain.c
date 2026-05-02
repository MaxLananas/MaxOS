#include "screen.h"
#include "keyboard.h"
#include "terminal.h"
#include "idt.h"
#include "timer.h"
#include "memory.h"
#include "paging.h"
#include "mouse.h"

void kmain(void) {
    screen_init();
    idt_init();
    timer_init(100);
    keyboard_init();
    mouse_init();
    paging_init();
    mem_init(1024 * 1024);
    heap_init((void*)0xC0000000, 1024 * 1024);
    terminal_init();
    terminal_run();
    for (;;);
}