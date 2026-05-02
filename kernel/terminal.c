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
        char c = keyboard_getchar();
        if (c == '\n') {
            cmd[pos] = 0;
            terminal_process(cmd);
            pos = 0;
        } else if (c != 0) {
            if (pos < 255) {
                cmd[pos++] = c;
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