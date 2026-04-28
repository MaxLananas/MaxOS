#include "kernel/screen.h"
#include "kernel/keyboard.h"
#include "kernel/terminal.h"
#include "kernel/idt.h"
#include "kernel/timer.h"
#include "kernel/memory.h"

void kmain(void) {
    screen_init();
    screen_clear();
    idt_init();
    keyboard_init();
    timer_init(100);
    mem_init(1024 * 1024);
    terminal_init();
    terminal_run();
}