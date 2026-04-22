#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "idt.h"
#include "irq.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    idt_init();
    irq_init();
    keyboard_init();
    timer_init(100);
    terminal_init();
    terminal_run();
}