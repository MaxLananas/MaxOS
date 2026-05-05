#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0F);
}

void terminal_run(void) {
    while (1) {
        char c = keyboard_getchar();
        if (c) {
            screen_putchar(c, 0x0F);
        }
    }
}

void terminal_process(const char *cmd) {
}