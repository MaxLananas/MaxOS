#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "idt.h"
#include "irq.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    idt_init();
    idt_load();
    keyboard_init();
    timer_init(100);
    terminal_init();
    terminal_run();
}