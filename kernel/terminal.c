#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal ready", 0x0A);
}

void terminal_run(void) {
    char buffer[256];
    unsigned int index = 0;

    while (1) {
        char c = keyboard_getchar();
        if (c == '\n') {
            buffer[index] = '\0';
            terminal_process(buffer);
            screen_writeln("", 0x07);
            index = 0;
        } else if (c == '\b') {
            if (index > 0) {
                index--;
                screen_putchar('\b', 0x07);
                screen_putchar(' ', 0x07);
                screen_putchar('\b', 0x07);
            }
        } else if (c >= ' ') {
            buffer[index++] = c;
            screen_putchar(c, 0x07);
        }
    }
}

void terminal_process(const char *cmd) {
    if (strcmp(cmd, "help") == 0) {
        screen_writeln("Available commands:", 0x0A);
        screen_writeln("  help - Show this help", 0x0A);
        screen_writeln("  clear - Clear the screen", 0x0A);
    } else if (strcmp(cmd, "clear") == 0) {
        screen_clear();
    } else {
        screen_writeln("Unknown command", 0x0C);
    }
}

int strcmp(const char *s1, const char *s2) {
    while (*s1 && (*s1 == *s2)) {
        s1++;
        s2++;
    }
    return *(unsigned char*)s1 - *(unsigned char*)s2;
}