#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

#define MAX_CMD_LEN 100

char cmd_buffer[MAX_CMD_LEN];
unsigned int cmd_pos = 0;

void terminal_init(void) {
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    screen_writeln("Type 'help' for commands", 0x0F);

    while (1) {
        char c = keyboard_getchar();
        if (c == '\n') {
            screen_putchar('\n', 0x0F);
            cmd_buffer[cmd_pos] = '\0';
            terminal_process(cmd_buffer);
            cmd_pos = 0;
        } else if (c == '\b') {
            if (cmd_pos > 0) {
                cmd_pos--;
                screen_putchar('\b', 0x0F);
                screen_putchar(' ', 0x0F);
                screen_putchar('\b', 0x0F);
            }
        } else {
            if (cmd_pos < MAX_CMD_LEN - 1) {
                cmd_buffer[cmd_pos++] = c;
                screen_putchar(c, 0x0F);
            }
        }
    }
}

void terminal_process(const char *cmd) {
    if (strcmp(cmd, "help") == 0) {
        screen_writeln("Available commands:", 0x0A);
        screen_writeln("  help - Show this help", 0x0F);
        screen_writeln("  reboot - Reboot the system", 0x0F);
    } else if (strcmp(cmd, "reboot") == 0) {
        outb(0x64, 0xFE);
    } else {
        screen_writeln("Unknown command", 0x0C);
    }
}