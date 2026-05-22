#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "timer.h"
#include "fault_handler.h"
#include "mouse.h"
#include "paging.h"
#include "pmm.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x0F);

    idt_init();
    keyboard_init();
    timer_init(100);
    mouse_init();
    paging_init();

    screen_writeln("All systems initialized", 0x0A);
    screen_writeln("Type 'help' for commands", 0x09);

    terminal_init();
    terminal_run();
}