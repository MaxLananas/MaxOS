#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

#define MAX_CMD_LEN 100

char cmd_buffer[MAX_CMD_LEN];
unsigned int cmd_len = 0;

void terminal_init(void)
{
    screen_clear();
}

void terminal_run(void)
{
    while (1) {
        char c = keyboard_getchar();
        if (c) {
            if (c == '\n') {
                screen_putchar('\n', 0x07);
                cmd_buffer[cmd_len] = 0;
                terminal_process(cmd_buffer);
                cmd_len = 0;
            } else if (c == '\b') {
                if (cmd_len > 0) {
                    cmd_len--;
                    screen_putchar('\b', 0x07);
                }
            } else {
                cmd_buffer[cmd_len++] = c;
                screen_putchar(c, 0x07);
            }
        }
    }
}

void terminal_process(const char *cmd)
{
    screen_writeln("Command executed: ", 0x0A);
    screen_writeln(cmd, 0x07);
}