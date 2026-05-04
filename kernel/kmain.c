#include "screen.h"
#include "keyboard.h"
#include "terminal.h"
#include "idt.h"
#include "irq.h"
#include "timer.h"
#include "fault_handler.h"
#include "mouse.h"
#include "paging.h"

void kmain(void) {
    screen_init();
    idt_init();
    irq_init();
    keyboard_init();
    timer_init(100);
    mouse_init();
    paging_init();
    terminal_init();
    terminal_run();
}