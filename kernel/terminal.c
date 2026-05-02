#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0F);
}

void terminal_run(void) {
    char buffer[256];
    unsigned int pos = 0;
    char c;

    while (1) {
        c = keyboard_getchar();
        if (c) {
            if (c == '\n') {
                buffer[pos] = 0;
                screen_writeln(buffer, 0x0F);
                pos = 0;
            } else if (c == '\b') {
                if (pos > 0) {
                    pos--;
                    screen_putchar('\b', 0x0F);
                }
            } else {
                buffer[pos++] = c;
                screen_putchar(c, 0x0F);
            }
        }
    }
}

void terminal_process(const char *cmd) {
    // Command processing logic
}