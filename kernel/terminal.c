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
    while (1) {
        char c = keyboard_getchar();
        if (c) {
            if (c == '\n') {
                screen_putchar('\n', 0x0F);
                terminal_process(cmd_buffer);
                cmd_len = 0;
                screen_writeln("> ", 0x0F);
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
}

void terminal_process(const char *cmd) {
    screen_writeln("Command: ", 0x0F);
    screen_writeln(cmd, 0x0F);
}