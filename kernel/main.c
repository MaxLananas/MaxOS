#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "idt.h"
#include "fault_handler.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_set_color(0x0F);
    screen_writeln("Bare Metal OS", 0x0A);
    screen_writeln("Initializing IDT...", 0x0F);

    idt_init();
    fault_handler_init();
    keyboard_init();
    timer_init(100);

    screen_writeln("IDT initialized", 0x0F);
    screen_writeln("Keyboard initialized", 0x0F);
    screen_writeln("Timer initialized", 0x0F);

    while (1) {
        char c = keyboard_getchar();
        if (c) {
            screen_putchar(c, 0x0F);
        }
    }
}