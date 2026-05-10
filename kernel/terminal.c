#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "timer.h"

#define MAX_CMD 256

char cmd_buffer[MAX_CMD];
unsigned int cmd_pos = 0;

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    while (1) {
        asm volatile("hlt");
    }
}

void terminal_process(const char *cmd) {
    if (*cmd == '\n') {
        cmd_buffer[cmd_pos] = '\0';
        screen_writeln(cmd_buffer, 0x0F);
        cmd_pos = 0;
    } else if (*cmd == '\b') {
        if (cmd_pos > 0) {
            cmd_pos--;
            screen_putchar(' ', 0x0F);
        }
    } else {
        if (cmd_pos < MAX_CMD - 1) {
            cmd_buffer[cmd_pos++] = *cmd;
            screen_putchar(*cmd, 0x0F);
        }
    }
}