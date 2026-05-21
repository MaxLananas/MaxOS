#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "timer.h"
#include "fault_handler.h"

void kmain(void) {
    screen_init();
    idt_init();
    timer_init(100);
    keyboard_init();

    screen_writeln("Kernel initialized", 0x0F);
    screen_writeln("Type something...", 0x0A);

    for (;;) {
        char c = keyboard_getchar();
        if (c) {
            screen_putchar(c, 0x0F);
        }
    }
}