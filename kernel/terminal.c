#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

#define MAX_CMD_LEN 64

static char cmd_buffer[MAX_CMD_LEN];
static unsigned int cmd_len = 0;

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    screen_writeln("Type 'help' for commands", 0x0A);
    while (1) {
        screen_putchar('>', 0x0F);
        cmd_len = 0;
        while (1) {
            char c = keyboard_getchar();
            if (c == '\n') {
                screen_putchar('\n', 0x0F);
                break;
            }
            if (cmd_len < MAX_CMD_LEN - 1) {
                cmd_buffer[cmd_len++] = c;
                screen_putchar(c, 0x0F);
            }
        }
        cmd_buffer[cmd_len] = '\0';
        terminal_process(cmd_buffer);
    }
}

void terminal_process(const char *cmd) {
    if (cmd[0] == '\0') return;

    if (cmd[0] == 'h' && cmd[1] == 'e' && cmd[2] == 'l' && cmd[3] == 'p') {
        screen_writeln("Available commands:", 0x0A);
        screen_writeln("  help - Show this help", 0x0A);
        screen_writeln("  clear - Clear screen", 0x0A);
    } else if (cmd[0] == 'c' && cmd[1] == 'l' && cmd[2] == 'e' && cmd[3] == 'a' && cmd[4] == 'r') {
        screen_clear();
    } else {
        screen_writeln("Unknown command", 0x0C);
    }
}