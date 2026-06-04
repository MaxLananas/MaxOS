#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

#define MAX_CMD_LEN 64

static char cmd_buffer[MAX_CMD_LEN];
static unsigned int cmd_pos = 0;

void terminal_init(void) {
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    screen_writeln("Type 'help' for commands", 0x0A);

    for (;;) {
        char c = keyboard_getchar();
        if (c) {
            if (c == '\n') {
                cmd_buffer[cmd_pos] = 0;
                terminal_process(cmd_buffer);
                cmd_pos = 0;
            } else if (c == '\b') {
                if (cmd_pos > 0) {
                    cmd_pos--;
                    screen_putchar('\b', 0x0F);
                }
            } else {
                cmd_buffer[cmd_pos++] = c;
                screen_putchar(c, 0x0F);
            }
        }
    }
}

void terminal_process(const char *cmd) {
    screen_putchar('\n', 0x0F);

    if (cmd[0] == 0) {
        return;
    }

    if (cmd[0] == 'h' && cmd[1] == 'e' && cmd[2] == 'l' && cmd[3] == 'p') {
        screen_writeln("Available commands:", 0x0A);
        screen_writeln("help - Show this help", 0x0A);
        screen_writeln("clear - Clear screen", 0x0A);
    } else if (cmd[0] == 'c' && cmd[1] == 'l' && cmd[2] == 'e' && cmd[3] == 'a' && cmd[3] == 'r') {
        screen_clear();
    } else {
        screen_writeln("Unknown command", 0x0C);
    }
}