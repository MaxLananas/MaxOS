#include "../drivers/screen.h"
#include "../kernel/idt.h"
#include "../kernel/timer.h"
#include "../kernel/keyboard.h"
#include "../kernel/terminal.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_set_color(0x0F);
    screen_writeln("Booting...", 0x0F);

    idt_init();
    timer_init(100);
    keyboard_init();
    terminal_init();

    terminal_run();
}