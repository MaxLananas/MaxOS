#include "screen.h"
#include "keyboard.h"
#include "terminal.h"

void terminal_init(void) {
    screen_init();
    keyboard_init();
}

void terminal_run(void) {
    while (1) {
        char c = keyboard_getchar();
        if (c != 0) {
            screen_putchar(c, 0x0F);
        }
    }
}

void terminal_process(const char *cmd) {
    screen_writeln(cmd, 0x0F);
}