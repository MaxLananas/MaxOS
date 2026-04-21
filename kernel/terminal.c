#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

#define MAX_CMD_LEN 128

static char cmd_buffer[MAX_CMD_LEN];
static unsigned int cmd_pos = 0;

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    while (1) {
        char c = keyboard_getchar();
        if (c) {
            if (c == '\n') {
                cmd_buffer[cmd_pos] = 0;
                terminal_process(cmd_buffer);
                cmd_pos = 0;
            } else if (c == '\b') {
                if (cmd_pos > 0) {
                    cmd_pos--;
                    screen_putchar('\b', 0x07);
                }
            } else if (cmd_pos < MAX_CMD_LEN - 1) {
                cmd_buffer[cmd_pos++] = c;
                screen_putchar(c, 0x07);
            }
        }
    }
}

void terminal_process(const char *cmd) {
    screen_writeln("", 0x07);
    screen_writeln("Command not recognized", 0x0C);
    screen_writeln("", 0x07);
}