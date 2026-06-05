#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal ready", 0x0A);
}

void terminal_run(void) {
    char cmd[256];
    unsigned int pos = 0;
    char c;

    while (1) {
        c = keyboard_getchar();
        if (c) {
            if (c == '\n') {
                cmd[pos] = 0;
                screen_putchar('\n', 0x0F);
                terminal_process(cmd);
                pos = 0;
            } else if (c == '\b') {
                if (pos > 0) {
                    pos--;
                    screen_putchar('\b', 0x0F);
                    screen_putchar(' ', 0x0F);
                    screen_putchar('\b', 0x0F);
                }
            } else {
                cmd[pos++] = c;
                screen_putchar(c, 0x0F);
            }
        }
    }
}

void terminal_process(const char *cmd) {
    screen_writeln("Command executed:", 0x0A);
    screen_writeln(cmd, 0x0F);
}