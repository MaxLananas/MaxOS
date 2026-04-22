#include "drivers/screen.h"
#include "drivers/keyboard.h"
#include "kernel/idt.h"
#include "kernel/timer.h"
#include "kernel/memory.h"
#include "apps/terminal.h"

void kmain(void) {
    screen_init();
    screen_clear();
    mem_init(32768);
    idt_init();
    timer_init(100);
    keyboard_init();
    __asm__ volatile("sti");
    terminal_init();
    terminal_run();
}
