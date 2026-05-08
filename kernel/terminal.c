#include "drivers/screen.h"
#include "kernel/keyboard.h"
#include "kernel/terminal.h"

void terminal_init(void) {
    screen_init();
    keyboard_init();
}

void terminal_run(void) {
    screen_clear();
    screen_writeln("Terminal ready", 0x0F);
}

void terminal_process(const char *cmd) {
    screen_writeln(cmd, 0x0F);
}