#include "terminal.h"
#include "screen.h"

void terminal_init(void) {
    screen_init();
}

void terminal_run(void) {
    char buffer[256];
    int i = 0;
    char c;

    while (1) {
        c = keyboard_getchar();
        if (c == '\n') {
            buffer[i] = 0;
            terminal_process(buffer);
            screen_writeln("", 0x0F);
            i = 0;
        } else if (c == '\b' && i > 0) {
            i--;
            screen_putchar(' ', 0x0F);
            screen_putchar('\b', 0x0F);
        } else if (i < 255) {
            screen_putchar(c, 0x0F);
            buffer[i++] = c;
        }
    }
}

void terminal_process(const char *cmd) {
    if (cmd[0] == 'h' && cmd[1] == 'e' && cmd[2] == 'l' && cmd[3] == 'p' && cmd[4] == 0) {
        screen_writeln("Available commands:", 0x0F);
        screen_writeln("  help - Show this help", 0x0F);
    } else {
        screen_writeln("Unknown command. Type 'help' for help.", 0x0F);
    }
}