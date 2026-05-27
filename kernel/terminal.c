#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

void terminal_init(void) {
    screen_clear();
}

void terminal_run(void) {
    char cmd[256];
    unsigned int pos = 0;

    screen_putchar('>', 0x0A);
    screen_putchar(' ', 0x0A);

    while(1) {
        char c = keyboard_getchar();
        if (c == '\n') {
            cmd[pos] = 0;
            screen_putchar('\n', 0x0A);
            terminal_process(cmd);
            pos = 0;
            screen_putchar('>', 0x0A);
            screen_putchar(' ', 0x0A);
        } else if (c == '\b') {
            if (pos > 0) {
                pos--;
                screen_putchar('\b', 0x0A);
            }
        } else {
            cmd[pos++] = c;
            screen_putchar(c, 0x0A);
        }
    }
}

void terminal_process(const char *cmd) {
    screen_writeln("Command executed: ", 0x0A);
    screen_writeln(cmd, 0x0A);
}