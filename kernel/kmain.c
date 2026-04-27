#include "screen.h"
#include "keyboard.h"
#include "terminal.h"
#include "idt.h"
#include "timer.h"
#include "memory.h"

void kmain(void) {
    screen_init();
    screen_clear();

    idt_init();
    keyboard_init();
    timer_init(100);
    mem_init(1024 * 1024); // 1MB

    terminal_init();
    terminal_run();
}