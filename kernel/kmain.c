#include "screen.h"
#include "keyboard.h"
#include "terminal.h"
#include "idt.h"
#include "isr.h"
#include "irq.h"
#include "timer.h"
#include "mouse.h"
#include "paging.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x0F);

    idt_init();
    isr_init();
    irq_init();
    timer_init(100);
    keyboard_init();
    mouse_init();
    paging_init();

    terminal_init();
    terminal_run();
}