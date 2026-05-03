#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

#define MAX_CMD 128

char cmd_buffer[MAX_CMD];
unsigned int cmd_pos = 0;

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    screen_writeln("> ", 0x0A);
    cmd_pos = 0;
}

void terminal_process(const char *cmd) {
    if (strcmp(cmd, "help") == 0) {
        screen_writeln("Available commands: help, clear, reboot", 0x0A);
    } else if (strcmp(cmd, "clear") == 0) {
        screen_clear();
    } else if (strcmp(cmd, "reboot") == 0) {
        outb(0x64, 0xFE);
    } else {
        screen_writeln("Unknown command", 0x0C);
    }
}