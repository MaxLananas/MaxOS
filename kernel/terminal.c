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
    unsigned int pos = 0;

    while (1) {
        screen_putchar('>', 0x0F);
        screen_putchar(' ', 0x0F);

        pos = 0;
        while (1) {
            char c = keyboard_getchar();
            if (c == '\n') {
                cmd[pos] = 0;
                screen_writeln("", 0x0F);
                break;
            } else if (c == '\b' && pos > 0) {
                pos--;
                screen_putchar('\b', 0x0F);
                screen_putchar(' ', 0x0F);
                screen_putchar('\b', 0x0F);
            } else if (c >= ' ' && c <= '~') {
                cmd[pos++] = c;
                screen_putchar(c, 0x0F);
            }
        }

        terminal_process(cmd);
    }
}

void terminal_process(const char *cmd) {
    if (cmd[0] == 0) return;

    screen_writeln("Command executed:", 0x0E);
    screen_writeln(cmd, 0x0F);
}