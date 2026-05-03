#include "screen.h"
#include "keyboard.h"
#include "terminal.h"
#include "idt.h"
#include "irq.h"
#include "timer.h"
#include "mouse.h"
#include "paging.h"

void kmain(void) {
    screen_init();
    idt_init();
    irq_init();
    timer_init(100);
    keyboard_init();
    mouse_init();
    paging_init();
    terminal_init();
    terminal_run();
}