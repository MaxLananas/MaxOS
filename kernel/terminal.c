#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

void terminal_init(void) {
    screen_init();
    keyboard_init();
}

void terminal_run(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0F);
    terminal_process("");
}

void terminal_process(const char *cmd) {
    // Simple terminal processing
    screen_putchar('>', 0x0F);
}