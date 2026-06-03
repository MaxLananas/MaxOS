#include "screen.h"
#include "keyboard.h"
#include "mouse.h"
#include "timer.h"
#include "idt.h"
#include "mem.h"
#include "paging.h"
#include "heap.h"

void kmain(void)
{
    screen_init();
    keyboard_init();
    mouse_init();
    timer_init(100);
    idt_init();
    mem_init(1024);
    paging_init();
    heap_init((void *)0x100000, 1024 * 1024);

    screen_writeln("Kernel started", 0x0A);
    for (;;);
}