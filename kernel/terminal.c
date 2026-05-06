#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

#define MAX_CMD_LEN 100

char cmd_buffer[MAX_CMD_LEN];
unsigned int cmd_len = 0;

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    screen_writeln("> ", 0x0F);
}

void terminal_process(const char *cmd) {
    if (cmd_len < MAX_CMD_LEN - 1) {
        cmd_buffer[cmd_len++] = *cmd;
        screen_putchar(*cmd, 0x0F);
    }
}