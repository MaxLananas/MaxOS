#include "terminal.h"
#include "keyboard.h"
#include "../screen.h"

#define MAX_CMD 64

void terminal_init(void) {
    screen_init();
    screen_writeln("Terminal initialized", 0x0A);
}

void terminal_run(void) {
    char cmd[MAX_CMD] = {0};
    unsigned int pos = 0;

    while(1) {
        char c = keyboard_getchar();
        if(c) {
            if(c == '\n') {
                screen_putchar('\n', 0x0F);
                terminal_process(cmd);
                pos = 0;
                cmd[0] = 0;
            } else if(c == '\b') {
                if(pos > 0) {
                    pos--;
                    screen_putchar('\b', 0x0F);
                }
            } else {
                if(pos < MAX_CMD - 1) {
                    cmd[pos++] = c;
                    screen_putchar(c, 0x0F);
                }
            }
        }
    }
}

void terminal_process(const char *cmd) {
    screen_writeln("Command: ", 0x0F);
    screen_writeln(cmd, 0x0F);
}