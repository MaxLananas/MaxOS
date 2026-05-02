#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

void terminal_init(void) {
    screen_init();
}

void terminal_run(void) {
    screen_writeln("Terminal ready", 0x0A);
}

void terminal_process(const char *cmd) {
    (void)cmd;
}