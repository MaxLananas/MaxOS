#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

void terminal_init(void) {
    screen_init();
}

void terminal_run(void) {
    char cmd[256];
    int pos = 0;
    while(1) {
        char c = keyboard_getchar();
        if (c == '\n') {
            cmd[pos] = '\0';
            terminal_process(cmd);
            pos = 0;
        } else {
            cmd[pos++] = c;
            screen_putchar(c, 0x0F);
        }
    }
}

void terminal_process(const char *cmd) {
    screen_writeln(cmd, 0x0F);
}