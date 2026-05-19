#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

void terminal_init(void) {
    screen_clear();
    screen_write("Terminal ready", 0x0A);
    screen_putchar('\n', 0x0A);
}

void terminal_run(void) {
    char buffer[256];
    int index = 0;

    while (1) {
        char c = keyboard_getchar();

        if (c == '\n') {
            buffer[index] = '\0';
            terminal_process(buffer);
            index = 0;
            screen_write("\n> ", 0x0F);
        } else if (c == '\b') {
            if (index > 0) {
                index--;
                screen_putchar(' ', 0x0F);
                move_cursor();
            }
        } else {
            buffer[index++] = c;
            screen_putchar(c, 0x0F);
        }
    }
}

void terminal_process(const char *cmd) {
    if (cmd[0] == 'h' && cmd[1] == 'e' && cmd[2] == 'l' && cmd[3] == 'p') {
        screen_writeln("Available commands:", 0x0A);
        screen_writeln("- help: Show this help", 0x0A);
        screen_writeln("- clear: Clear screen", 0x0A);
    } else if (cmd[0] == 'c' && cmd[1] == 'l' && cmd[2] == 'e' && cmd[3] == 'a' && cmd[4] == 'r') {
        screen_clear();
    } else {
        screen_writeln("Unknown command", 0x0C);
    }
}