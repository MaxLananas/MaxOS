#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

#define MAX_CMD_LEN 100

char cmd_buffer[MAX_CMD_LEN];
unsigned int cmd_len = 0;

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    screen_writeln("> ", 0x0F);
    terminal_process(cmd_buffer);
}

void terminal_process(const char *cmd) {
    if (strcmp(cmd, "help") == 0) {
        screen_writeln("Available commands:", 0x0A);
        screen_writeln("  help - Show this help", 0x0F);
    } else {
        screen_writeln("Unknown command", 0x0C);
    }
    cmd_len = 0;
}