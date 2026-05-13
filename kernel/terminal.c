#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

#define MAX_CMD_LEN 100

static char cmd_buffer[MAX_CMD_LEN];
static unsigned int cmd_len = 0;

void terminal_init(void)
{
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void)
{
    screen_writeln("Type 'help' for commands", 0x0A);

    for (;;) {
        terminal_process(keyboard_getchar());
    }
}

void terminal_process(char c)
{
    if (c == '\n') {
        screen_putchar('\n', 0x0F);
        cmd_buffer[cmd_len] = '\0';

        if (cmd_len > 0) {
            if (strcmp(cmd_buffer, "help") == 0) {
                screen_writeln("Available commands:", 0x0A);
                screen_writeln("  help - Show this help", 0x0A);
            } else {
                screen_writeln("Unknown command", 0x0C);
            }
            cmd_len = 0;
        }
    } else if (c == '\b') {
        if (cmd_len > 0) {
            cmd_len--;
            screen_putchar('\b', 0x0F);
            screen_putchar(' ', 0x0F);
            screen_putchar('\b', 0x0F);
        }
    } else if (cmd_len < MAX_CMD_LEN - 1) {
        cmd_buffer[cmd_len++] = c;
        screen_putchar(c, 0x0F);
    }
}