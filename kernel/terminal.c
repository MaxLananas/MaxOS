#include "screen.h"

void terminal_init(void) {
    screen_init();
}

void terminal_run(void) {
    while (1) {
        asm volatile("hlt");
    }
}

void terminal_process(const char *cmd) {
    (void)cmd;
}