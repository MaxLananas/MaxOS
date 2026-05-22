#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

void terminal_init() {
    screen_init();
    keyboard_init();
}

void terminal_run() {
    screen_writeln("Terminal ready", 0x0A);
}

void terminal_process(const char *cmd) {
    screen_putchar(*cmd, 0x0F);
}