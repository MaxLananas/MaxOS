#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

#define MAX_CMD_LEN 128

char cmd_buffer[MAX_CMD_LEN];
unsigned int cmd_pos = 0;

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    screen_writeln("> ", 0x0F);
}

void terminal_process(const char *cmd) {
    screen_writeln(cmd, 0x0F);
    screen_putchar('\n', 0x0F);
}