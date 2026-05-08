#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

void terminal_init(void) {
    screen_init();
    keyboard_init();
}

void terminal_run(void) {
    screen_writeln("Terminal ready", 0x0A);
}

void terminal_process(const char *cmd) {
    screen_writeln(cmd, 0x0F);
}