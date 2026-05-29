#include "terminal_process.h"
#include "terminal.h"
#include "screen.h"

void terminal_process(const char *cmd) {
    screen_writeln(cmd, 0x0F);
    screen_putchar('\n', 0x0F);
}