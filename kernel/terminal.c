#include "screen.h"
#include "keyboard.h"
#include "string.h"

void terminal_init(void) {
    screen_init();
    keyboard_init();
}

void terminal_run(void) {
    screen_clear();
    screen_writeln("Terminal started", 0x0F);
}

void terminal_process(const char *cmd) {
    screen_writeln(cmd, 0x0F);
}