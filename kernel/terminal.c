#include "keyboard.h"
#include "screen.h"
#include "terminal.h"

void terminal_init(void) {
    screen_init();
}

void terminal_run(void) {
    terminal_process(0);
}

void terminal_process(const char *cmd) {
    screen_writeln("Terminal ready", 0x0F);
}