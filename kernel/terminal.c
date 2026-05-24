#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

void terminal_init(void) {
    screen_init();
    screen_clear();
    keyboard_init();
}

void terminal_run(void) {
    screen_writeln("Terminal initialized", 0x0F);
    terminal_process("");
}

void terminal_process(const char *cmd) {
    // Basic terminal processing
    char c;
    while ((c = keyboard_getchar()) != 0) {
        if (c == '\n') {
            screen_writeln("", 0x0F);
        } else {
            screen_putchar(c, 0x0F);
        }
    }
}