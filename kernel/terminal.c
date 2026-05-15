#include "screen.h"
#include "keyboard.h"
#include "terminal.h"

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal ready", 0x0F);
}

void terminal_run(void) {
    char cmd_buffer[256];
    unsigned int pos = 0;

    while (1) {
        char c = keyboard_getchar();
        if (c == '\n') {
            cmd_buffer[pos] = 0;
            terminal_process(cmd_buffer);
            pos = 0;
        } else if (c == '\b') {
            if (pos > 0) {
                pos--;
                screen_putchar('\b', 0x0F);
                screen_putchar(' ', 0x0F);
                screen_putchar('\b', 0x0F);
            }
        } else {
            cmd_buffer[pos++] = c;
            screen_putchar(c, 0x0F);
        }
    }
}

void terminal_process(const char *cmd) {
    screen_writeln(cmd, 0x0A);
}