#include "terminal.h"
#include "screen.h"
#include "keyboard.h"

void terminal_init(void) {
    screen_init();
}

void terminal_run(void) {
    char c;
    while (1) {
        c = keyboard_getchar();
        if (c) {
            screen_putchar(c, 0x0F);
        }
    }
}

void terminal_process(const char *cmd) {
}