#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    screen_writeln("> ", 0x0A);
}

void terminal_process(const char *cmd) {
    screen_writeln(cmd, 0x0F);
    screen_writeln("\n> ", 0x0A);
}