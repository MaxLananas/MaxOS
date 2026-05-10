#include "kmain.h"
#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "irq.h"
#include "timer.h"
#include "fault_handler.h"
#include "mouse.h"
#include "paging.h"
#include "mem.h"

void kmain(void) {
    screen_init();
    screen_clear();

    idt_init();
    irq_init();
    timer_init(100);
    keyboard_init();
    mouse_init();
    paging_init();
    mem_init(1024);

    screen_writeln("Kernel initialized", 0x0A);
    screen_writeln("Type commands below:", 0x0B);

    terminal_init();
    terminal_run();
}