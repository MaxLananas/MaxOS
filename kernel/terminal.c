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
    screen_writeln("> ", 0x0F);
    while (1) {
        char c = keyboard_getchar();
        if (c) {
            if (c == '\n') {
                cmd[pos] = 0;
                screen_writeln("", 0x0F);
                terminal_process(cmd);
                pos = 0;
                screen_writeln("> ", 0x0F);
            } else {
                cmd[pos++] = c;
                screen_putchar(c, 0x0F);
            }
        }
    }
}

void terminal_process(const char *cmd) {
    screen_writeln(cmd, 0x0A);
}