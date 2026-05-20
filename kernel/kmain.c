#include "kmain.h"
#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "idt.h"
#include "mouse.h"

void kmain(void) {
    screen_init();
    keyboard_init();
    timer_init(100);
    mouse_init();
    idt_init();

    screen_writeln("Kernel initialized", 0x0A);
    terminal_run();
}