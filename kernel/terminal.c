#include "terminal.h"
#include "keyboard.h"
#include "screen.h"

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    char buffer[100];
    int index = 0;
    char c;

    while (1) {
        c = keyboard_getchar();
        if (c == '\n') {
            buffer[index] = 0;
            terminal_process(buffer);
            index = 0;
            screen_write("> ", 0x0F);
        } else if (c == '\b') {
            if (index > 0) {
                index--;
                screen_putchar('\b', 0x0F);
                screen_putchar(' ', 0x0F);
                screen_putchar('\b', 0x0F);
            }
        } else {
            buffer[index] = c;
            index++;
            screen_putchar(c, 0x0F);
        }
    }
}

void terminal_process(const char *cmd) {
    screen_putchar('\n', 0x0F);
    screen_write("Command: ", 0x0A);
    screen_writeln(cmd, 0x0A);
}