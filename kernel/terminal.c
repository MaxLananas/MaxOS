#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

static char command_buffer[256];
static unsigned int command_pos = 0;

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    screen_writeln("> ", 0x0F);
    while (1) {
        char c = keyboard_getchar();
        if (c) {
            if (c == '\n') {
                screen_putchar('\n', 0x0F);
                command_buffer[command_pos] = 0;
                terminal_process(command_buffer);
                command_pos = 0;
            } else if (c == '\b') {
                if (command_pos > 0) {
                    command_pos--;
                    screen_putchar('\b', 0x0F);
                }
            } else {
                command_buffer[command_pos++] = c;
                screen_putchar(c, 0x0F);
            }
        }
    }
}

void terminal_process(const char *cmd) {
    screen_writeln("Command: ", 0x0F);
    screen_writeln(cmd, 0x0F);
}