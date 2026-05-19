#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

void terminal_init(void) {
    screen_init();
    keyboard_init();
}

void terminal_run(void) {
    screen_writeln("Terminal ready", 0x0A);
    char cmd[256];
    unsigned int pos = 0;

    while (1) {
        char c = keyboard_getchar();
        if (c == '\n') {
            cmd[pos] = 0;
            screen_putchar('\n', 0x0F);
            terminal_process(cmd);
            pos = 0;
        } else {
            cmd[pos++] = c;
            screen_putchar(c, 0x0F);
        }
    }
}

void terminal_process(const char *cmd) {
    screen_writeln("Command executed:", 0x0B);
    screen_writeln(cmd, 0x0F);
}