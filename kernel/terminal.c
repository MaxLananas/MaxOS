#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "terminal_process.h"

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0F);
}

void terminal_run(void) {
    char cmd[256];
    unsigned int pos = 0;
    char c;

    while (1) {
        c = keyboard_getchar();
        if (c == '\n') {
            cmd[pos] = 0;
            screen_writeln("", 0x0F);
            terminal_process(cmd);
            pos = 0;
        } else if (c == '\b') {
            if (pos > 0) {
                pos--;
                screen_putchar('\b', 0x0F);
            }
        } else {
            cmd[pos++] = c;
            screen_putchar(c, 0x0F);
        }
    }
}