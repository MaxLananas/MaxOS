#include "drivers/screen.h"
#include "drivers/keyboard.h"
#include "kernel/terminal.h"

void terminal_init(void) {
    screen_init();
    keyboard_init();
}

void terminal_run(void) {
    screen_writeln("Terminal ready", 0x0A);
    while (1) {
        char c = keyboard_getchar();
        if (c) {
            screen_putchar(c, 0x0F);
        }
    }
}

void terminal_process(const char *cmd) {
}