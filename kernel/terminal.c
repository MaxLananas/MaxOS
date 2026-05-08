#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

#define MAX_CMD 128

static char cmd_buffer[MAX_CMD];
static unsigned int cmd_pos = 0;

void terminal_init(void) {
    screen_init();
    keyboard_init();
    screen_clear();
    screen_writeln("Terminal initialized", 0x0F);
}

void terminal_run(void) {
    while (1) {
        char c = keyboard_getchar();
        if (c) {
            if (c == '\n') {
                cmd_buffer[cmd_pos] = '\0';
                terminal_process(cmd_buffer);
                cmd_pos = 0;
            } else if (c == '\b') {
                if (cmd_pos > 0) {
                    cmd_pos--;
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
    screen_writeln("", 0x0F);
    screen_writeln("Processing command:", 0x0A);
    screen_writeln(cmd, 0x0F);
    screen_writeln("", 0x0F);
}