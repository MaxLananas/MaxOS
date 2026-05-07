#include "idt.h"
#include "screen.h"
#include "keyboard.h"
#include "timer.h"

void kmain(void) {
    screen_init();
    screen_write("Initializing IDT...", 0x0A);
    idt_init();
    screen_writeln("OK", 0x0A);

    screen_write("Initializing keyboard...", 0x0A);
    keyboard_init();
    screen_writeln("OK", 0x0A);

    screen_write("Initializing timer...", 0x0A);
    timer_init(100);
    screen_writeln("OK", 0x0A);

    screen_writeln("System ready.", 0x0A);
}