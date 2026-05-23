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
    while (1) {
        char c = keyboard_getchar();
        if (c != 0) {
            screen_putchar(c, 0x0F);
        }
    }
}

void terminal_process(const char *cmd) {
    // Implementation to be added
}