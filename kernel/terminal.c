#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    screen_writeln("> ", 0x0F);
    char cmd[256];
    unsigned int pos = 0;

    while (1) {
        char c = keyboard_getchar();
        if (c == '\n') {
            cmd[pos] = 0;
            terminal_process(cmd);
            screen_writeln("> ", 0x0F);
            pos = 0;
        } else if (c != 0) {
            cmd[pos++] = c;
            screen_putchar(c, 0x0F);
        }
    }
}

void terminal_process(const char *cmd) {
    screen_writeln(cmd, 0x0F);
}
```=== END FILE ===