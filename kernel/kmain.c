#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "timer.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    keyboard_init();
    idt_init();
    timer_init(100);
    terminal_init();

    screen_writeln("Kernel started successfully", 0x0A);
}