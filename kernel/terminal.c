#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

void terminal_init(void) {
    screen_clear();
}

void terminal_run(void) {
    screen_set_color(0x0F);
    screen_writeln("Terminal ready", 0x0A);
}

void terminal_process(const char *cmd) {
    if (cmd[0] == 'h' && cmd[1] == 'e' && cmd[2] == 'l' && cmd[3] == 'p') {
        screen_writeln("Available commands:", 0x0A);
        screen_writeln("  help - Show this help", 0x0F);
    } else {
        screen_writeln("Unknown command", 0x0C);
    }
}