#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

void terminal_init() {
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run() {
}

void terminal_process(const char *cmd) {
}