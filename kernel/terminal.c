#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "string.h"

#define MAX_CMD_LEN 128

static char cmd_buffer[MAX_CMD_LEN];
static unsigned int cmd_pos = 0;

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    screen_putchar('>', 0x0A);
}

void terminal_process(const char *cmd) {
    screen_writeln(cmd, 0x0F);
    cmd_pos = 0;
}