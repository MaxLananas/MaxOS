#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

#define MAX_CMD_LEN 100

char cmd_buffer[MAX_CMD_LEN];
unsigned int cmd_len = 0;

void terminal_init() {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run() {
    screen_writeln("> ", 0x0F);
    terminal_process(cmd_buffer);
}

void terminal_process(const char *cmd) {
    if (cmd_len == 0) return;

    if (cmd[0] == 'h' && cmd[1] == 'e' && cmd[2] == 'l' && cmd[3] == 'p') {
        screen_writeln("Available commands: help, clear", 0x0A);
    } else if (cmd[0] == 'c' && cmd[1] == 'l' && cmd[2] == 'e' && cmd[3] == 'a' && cmd[4] == 'r') {
        screen_clear();
    } else {
        screen_writeln("Unknown command", 0x0C);
    }

    cmd_len = 0;
}