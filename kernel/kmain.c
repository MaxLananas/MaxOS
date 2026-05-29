#include "screen.h"
#include "keyboard.h"
#include "mouse.h"
#include "timer.h"
#include "idt.h"
#include "irq.h"
#include "mem.h"
#include "heap.h"
#include "paging.h"

void kmain() {
    screen_init();
    idt_init();
    keyboard_init();
    mouse_init();
    timer_init(100);
    mem_init(1024);
    heap_init((void*)0x100000, 1024 * 1024);
    paging_init();

    screen_writeln("Kernel started", 0x0A);
    while(1);
}