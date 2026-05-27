#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "idt.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_set_color(0x0F);
    screen_writeln("Booting...", 0x0F);

    idt_init();
    timer_init(100);
    keyboard_init();
    terminal_init();

    screen_writeln("Ready.", 0x0F);
    terminal_run();
}