#include "screen.h"
#include "idt.h"
#include "timer.h"
#include "keyboard.h"
#include "log.h"
#include "terminal.h"
#include "mouse.h"
#include "memory.h"

void kmain(void) {
    screen_init();
    idt_init();
    timer_init(1000);
    keyboard_init();
    log_init();
    terminal_init();
    mouse_init();
    mem_init(0x100000, 0x4000000);

    terminal_run();
}