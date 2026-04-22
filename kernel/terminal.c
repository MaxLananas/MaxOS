#include "terminal.h"
#include "../drivers/screen.h"
#include "../drivers/keyboard.h"

void terminal_init(void) {
    screen_clear();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    screen_writeln("Terminal running...", 0x0F);
    while (1) {
        char c = keyboard_getchar();
        if (c) {
            screen_putchar(c, 0x0F);
        }
    }
}

void terminal_process(const char *cmd) {
    (void)cmd;
}