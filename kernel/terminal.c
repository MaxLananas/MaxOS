#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

#define MAX_CMD_LEN 100

static char cmd_buffer[MAX_CMD_LEN];
static unsigned int cmd_len = 0;

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    screen_writeln("Type 'help' for commands", 0x0F);

    while (1) {
        char c = keyboard_getchar();
        if (c == '\n') {
            screen_putchar('\n', 0x0F);
            cmd_buffer[cmd_len] = '\0';
            terminal_process(cmd_buffer);
            cmd_len = 0;
        } else if (c == '\b') {
            if (cmd_len > 0) {
                cmd_len--;
                screen_putchar('\b', 0x0F);
                screen_putchar(' ', 0x0F);
                screen_putchar('\b', 0x0F);
            }
        } else {
            if (cmd_len < MAX_CMD_LEN - 1) {
                cmd_buffer[cmd_len++] = c;
                screen_putchar(c, 0x0F);
            }
        }
    }
}

void terminal_process(const char *cmd) {
    if (cmd_len == 0) return;

    if (cmd[0] == 'h' && cmd[1] == 'e' && cmd[2] == 'l' && cmd[3] == 'p') {
        screen_writeln("Available commands:", 0x0A);
        screen_writeln("help - Show this help", 0x0F);
        screen_writeln("clear - Clear screen", 0x0F);
        screen_writeln("reboot - Reboot system", 0x0F);
    } else if (cmd[0] == 'c' && cmd[1] == 'l' && cmd[2] == 'e' && cmd[3] == 'a' && cmd[4] == 'r') {
        screen_clear();
    } else if (cmd[0] == 'r' && cmd[1] == 'e' && cmd[2] == 'b' && cmd[3] == 'o' && cmd[4] == 'o' && cmd[5] == 't') {
        screen_writeln("Rebooting...", 0x0A);
        // TODO: Implement reboot
    } else {
        screen_writeln("Unknown command", 0x0C);
    }
}