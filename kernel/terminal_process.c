#include "terminal_process.h"
#include "terminal.h"
#include "screen.h"

void terminal_process(const char *cmd) {
    if (strcmp(cmd, "help") == 0) {
        screen_writeln("Available commands:", 0x0A);
        screen_writeln("  help - Show this help", 0x0F);
    } else {
        screen_writeln("Unknown command", 0x0C);
    }
}