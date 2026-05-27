#include "terminal_process.h"
#include "screen.h"
#include "terminal.h"

void terminal_process(const char *cmd) {
    screen_writeln(cmd, 0x0F);
}