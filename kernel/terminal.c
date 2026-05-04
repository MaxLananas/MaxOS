#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

void terminal_init(void) {
    screen_init();
    screen_set_color(0x0F);
    screen_clear();
}

void terminal_run(void) {
    screen_writeln("Terminal ready", 0x0A);
}

void terminal_process(const char *cmd) {
    (void)cmd;
}