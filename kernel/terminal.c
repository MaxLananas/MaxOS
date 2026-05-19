#include "terminal.h"
#include "screen.h"

void terminal_init(void) {
    screen_init();
    screen_clear();
}

void terminal_run(void) {
    screen_writeln("Terminal started", 0x0F);
}

void terminal_process(const char *cmd) {
    screen_writeln(cmd, 0x0F);
}