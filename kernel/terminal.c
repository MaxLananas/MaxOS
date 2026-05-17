#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

#define MAX_CMD_LEN 100

static char cmd_buffer[MAX_CMD_LEN];
static unsigned int cmd_len = 0;

void terminal_init(void) {
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    screen_writeln("> ", 0x0A);
    for (;;) {
        char c = keyboard_getchar();
        if (c == '\n') {
            screen_putchar('\n', 0x0A);
            cmd_buffer[cmd_len] = '\0';
            terminal_process(cmd_buffer);
            cmd_len = 0;
            screen_writeln("> ", 0x0A);
        } else if (c == '\b') {
            if (cmd_len > 0) {
                cmd_len--;
                screen_putchar('\b', 0x0A);
            }
        } else {
            if (cmd_len < MAX_CMD_LEN - 1) {
                cmd_buffer[cmd_len++] = c;
                screen_putchar(c, 0x0A);
            }
        }
    }
}

void terminal_process(const char *cmd) {
    screen_writeln("Command: ", 0x0A);
    screen_writeln(cmd, 0x0A);
}