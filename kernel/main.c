#include "screen.h"
#include "timer.h"
#include "keyboard.h"
#include "mouse.h"
#include "fault_handler.h"
#include "terminal.h"
#include "idt.h"
#include "mem.h"

void kmain(void) {
    screen_init();
    screen_clear();

    idt_init();
    timer_init(100);
    keyboard_init();
    mouse_init();

    mem_init(1024 * 1024); // 1GB

    terminal_init();
    terminal_run();
}