#include "../drivers/screen.h"
#include "../kernel/keyboard.h"
#include "../kernel/terminal.h"

static char buffer[256];
static int buffer_index = 0;

void terminal_init(void) {
    screen_writeln("Terminal initialized", 0x0F);
}

void terminal_run(void) {
    screen_writeln("Type 'help' for commands", 0x0F);

    while (1) {
        screen_write("> ", 0x0F);

        buffer_index = 0;
        while (1) {
            char c = keyboard_getchar();
            if (c == '\n') {
                buffer[buffer_index] = 0;
                screen_putchar('\n', 0x0F);
                terminal_process(buffer);
                break;
            } else if (c == '\b') {
                if (buffer_index > 0) {
                    buffer_index--;
                    screen_putchar('\b', 0x0F);
                    screen_putchar(' ', 0x0F);
                    screen_putchar('\b', 0x0F);
                }
            } else {
                buffer[buffer_index++] = c;
                screen_putchar(c, 0x0F);
            }
        }
    }
}

void terminal_process(const char *cmd) {
    if (strcmp(cmd, "help") == 0) {
        screen_writeln("Available commands:", 0x0F);
        screen_writeln("  help - Show this help", 0x0F);
        screen_writeln("  clear - Clear screen", 0x0F);
    } else if (strcmp(cmd, "clear") == 0) {
        screen_clear();
    } else {
        screen_writeln("Unknown command", 0x0F);
    }
}