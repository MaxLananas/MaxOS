#include "terminal.h"
#include "idt.h"
#include "keyboard.h"
#include "screen.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_set_color(0x0F);
    screen_writeln("Kernel started", 0x0A);

    idt_init();
    keyboard_init();
    terminal_init();
    terminal_run();
}