#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "timer.h"
#include "fault_handler.h"
#include "mouse.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    idt_init();
    keyboard_init();
    timer_init(100);
    mouse_init();
    terminal_init();

    screen_writeln("Kernel started", 0x0A);

    while (1) {
        terminal_run();
    }
}