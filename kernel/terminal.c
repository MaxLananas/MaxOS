#include "kernel/screen.h"
#include "kernel/keyboard.h"
#include "kernel/terminal.h"

void terminal_init(void) {
    screen_set_color(0x0F);
    screen_clear();
}

void terminal_run(void) {
    while (1) {
        char c = keyboard_getchar();
        screen_putchar(c, 0x0F);
    }
}

void terminal_process(const char *cmd) {
}