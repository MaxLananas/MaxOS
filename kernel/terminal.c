#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "terminal_process.h"

#define MAX_CMD 256

static char cmd_buffer[MAX_CMD];
static unsigned int cmd_pos = 0;

void terminal_init() {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run() {
    screen_writeln("> ", 0x0F);
    while (1) {
        char c = keyboard_getchar();
        if (c) {
            if (c == '\n') {
                cmd_buffer[cmd_pos] = 0;
                terminal_process(cmd_buffer);
                cmd_pos = 0;
                screen_writeln("\n> ", 0x0F);
            } else if (c == '\b') {
                if (cmd_pos > 0) {
                    cmd_pos--;
                    screen_putchar(' ', 0x0F);
                    screen_putchar('\b', 0x0F);
                }
            } else {
                cmd_buffer[cmd_pos++] = c;
                screen_putchar(c, 0x0F);
            }
        }
    }
}

void terminal_process(const char *cmd) {
    // Process command
}