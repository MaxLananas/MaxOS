#include "kmain.h"
#include "../drivers/screen.h"
#include "idt.h"
#include "timer.h"
#include "keyboard.h"
#include "fault_handler.h"
#include "mouse.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    idt_init();
    timer_init(100);
    keyboard_init();
    mouse_init();
    terminal_init();

    screen_writeln("Kernel initialized", 0x0A);
    terminal_run();

    while (1);
}