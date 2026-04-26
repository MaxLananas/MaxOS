#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    while (1) {
        keyboard_handler();
    }
}

void terminal_process(const char *cmd) {
    screen_putchar(*cmd, 0x0F);
}