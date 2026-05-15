#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "mouse.h"
#include "terminal.h"
#include "idt.h"
#include "fault_handler.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x0F);

    idt_init();
    keyboard_init();
    timer_init(100);
    mouse_init();
    terminal_init();

    screen_writeln("All systems ready", 0x0A);
    terminal_run();
}