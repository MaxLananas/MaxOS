#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

void terminal_init(void)
{
    screen_writeln("Terminal initialized", 0x0F);
}

void terminal_run(void)
{
    screen_writeln("Terminal running", 0x0F);
}

void terminal_process(const char *cmd)
{
    screen_writeln(cmd, 0x0F);
}