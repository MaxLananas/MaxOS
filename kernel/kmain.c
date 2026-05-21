#include "kmain.h"
#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "timer.h"
#include "mouse.h"

void kmain(void) {
    screen_init();
    idt_init();
    keyboard_init();
    timer_init(100);
    mouse_init();
    screen_writeln("Kernel started", 0x0A);
    terminal_init();
    terminal_run();

    while (1) {
        char c = keyboard_getchar();
        if (c) {
            screen_putchar(c, 0x0F);
        }
    }
}