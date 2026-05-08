#include "screen.h"
#include "keyboard.h"
#include "terminal.h"

void kmain(void) {
    terminal_init();
    terminal_run();

    for (;;) {
        char c = keyboard_getchar();
        if (c) {
            screen_putchar(c, 0x0F);
        }
    }
}