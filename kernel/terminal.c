#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

#define MAX_CMD_LEN 64

static char cmd_buffer[MAX_CMD_LEN];
static unsigned int cmd_len = 0;

void terminal_init(void) {
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    screen_writeln("Type 'help' for commands", 0x0F);
    while (1) {
        asm volatile("hlt");
    }
}

void terminal_process(const char *cmd) {
    if (*cmd == '\n') {
        cmd_buffer[cmd_len] = '\0';
        screen_writeln(cmd_buffer, 0x0F);
        cmd_len = 0;
    } else if (*cmd == '\b') {
        if (cmd_len > 0) {
            cmd_len--;
            screen_putchar('\b', 0x0F);
        }
    } else {
        if (cmd_len < MAX_CMD_LEN - 1) {
            cmd_buffer[cmd_len++] = *cmd;
            screen_putchar(*cmd, 0x0F);
        }
    }
}