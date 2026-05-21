#include "kmain.h"
#include "screen.h"
#include "idt.h"
#include "timer.h"
#include "keyboard.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    idt_init();
    timer_init(100);
    keyboard_init();
    terminal_init();
    terminal_run();
    while (1);
}