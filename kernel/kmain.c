#include "screen.h"
#include "keyboard.h"
#include "terminal.h"
#include "idt.h"
#include "irq.h"
#include "timer.h"

void kmain(void) {
    screen_init();
    idt_init();
    irq_init();
    timer_init(100);
    keyboard_init();
    terminal_init();
    terminal_run();

    while(1);
}