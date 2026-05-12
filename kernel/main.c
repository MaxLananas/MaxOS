#include "screen.h"
#include "terminal.h"
#include "keyboard.h"
#include "idt.h"
#include "irq.h"
#include "timer.h"
#include "fault_handler.h"

void kmain() {
    screen_init();
    screen_clear();
    idt_init();
    irq_init();
    keyboard_init();
    timer_init(100);
    fault_handler_init();
    terminal_init();
    terminal_run();
}