#include "drivers/screen.h"
#include "kernel/timer.h"
#include "kernel/keyboard.h"
#include "kernel/idt.h"
#include "kernel/mouse.h"
#include "kernel/paging.h"
#include "kernel/mem.h"
#include "kernel/heap.h"

void kmain(void) {
    screen_init();
    idt_init();
    timer_init(100);
    keyboard_init();
    mouse_init();
    paging_init();
    mem_init(1024 * 1024);
    heap_init((void *)0xC0000000, 1024 * 1024);

    screen_writeln("Kernel initialized", 0x0A);
    screen_writeln("Welcome to Bare Metal OS", 0x0F);

    terminal_init();
    terminal_run();
}