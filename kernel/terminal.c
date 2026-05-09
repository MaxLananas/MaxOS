#include "screen.h"
#include "keyboard.h"
#include "terminal.h"

#define MAX_CMD 128

static char cmd_buffer[MAX_CMD];
static unsigned int cmd_pos = 0;

void terminal_init(void) {
    screen_init();
    screen_clear();
    screen_set_color(0x0F);
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    screen_writeln("> ", 0x0F);
    while (1) {
        char c = keyboard_getchar();
        if (c == '\n') {
            screen_writeln("", 0x0F);
            terminal_process(cmd_buffer);
            cmd_pos = 0;
            screen_writeln("> ", 0x0F);
        } else if (c == '\b') {
            if (cmd_pos > 0) {
                cmd_pos--;
                screen_putchar('\b', 0x0F);
                screen_putchar(' ', 0x0F);
                screen_putchar('\b', 0x0F);
            }
        } else if (cmd_pos < MAX_CMD - 1) {
            cmd_buffer[cmd_pos++] = c;
            screen_putchar(c, 0x0F);
        }
    }
}

void terminal_process(const char *cmd) {
    screen_writeln("Command: ", 0x0A);
    screen_writeln(cmd, 0x0F);
}