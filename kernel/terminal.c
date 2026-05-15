#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

#define MAX_CMD 128

static char cmd_buffer[MAX_CMD];
static unsigned int cmd_pos = 0;

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    screen_writeln("> ", 0x0F);
}

void terminal_process(const char *cmd) {
    screen_writeln(cmd, 0x0A);
    screen_writeln("\n> ", 0x0F);
}