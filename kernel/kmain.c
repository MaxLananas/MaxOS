#include "screen.h"
#include "keyboard.h"
#include "terminal.h"
#include "idt.h"
#include "isr.h"
#include "irq.h"
#include "timer.h"
#include "memory.h"
#include "paging.h"

void kmain(void) {
    screen_init();
    idt_init();
    isr_install();
    irq_install();
    timer_init(100);
    keyboard_init();
    terminal_init();
    paging_init();
    mem_init(1024 * 1024);

    screen_writeln("Kernel initialized", 0x0A);
    terminal_run();
}