#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "fault_handler.h"
#include "idt.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_set_color(0x0A);
    screen_writeln("Kernel started successfully!", 0x0A);

    idt_init();
    fault_handler_init();
    keyboard_init();
    timer_init(100);

    screen_writeln("IDT initialized", 0x0A);
    screen_writeln("Keyboard initialized", 0x0A);
    screen_writeln("Timer initialized", 0x0A);

    while (1) {
        char c = keyboard_getchar();
        if (c) {
            screen_putchar(c, 0x0F);
        }
    }
}