#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    char cmd[256];
    unsigned int cmd_pos = 0;

    while (1) {
        char c = keyboard_getchar();
        if (c) {
            if (c == '\n') {
                cmd[cmd_pos] = 0;
                terminal_process(cmd);
                cmd_pos = 0;
            } else if (c == '\b') {
                if (cmd_pos > 0) {
                    cmd_pos--;
                    screen_putchar('\b', 0x0F);
                    screen_putchar(' ', 0x0F);
                    screen_putchar('\b', 0x0F);
                }
            } else {
                cmd[cmd_pos++] = c;
                screen_putchar(c, 0x0F);
            }
        }
    }
}

void terminal_process(const char *cmd) {
    screen_writeln("", 0x0F);
    screen_writeln("Command:", 0x0A);
    screen_writeln(cmd, 0x0F);
    screen_writeln("", 0x0F);
}