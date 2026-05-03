#include "screen.h"
#include "keyboard.h"
#include "terminal.h"
#include "timer.h"
#include "mouse.h"
#include "idt.h"
#include "irq.h"

void kmain(void) {
    screen_init();
    idt_init();
    keyboard_init();
    timer_init(100);
    mouse_init();
    terminal_init();
    terminal_run();

    while (1) {
        char c = keyboard_getchar();
        if (c == '\n') {
            screen_putchar('\n', 0x07);
            terminal_process(cmd_buffer);
            cmd_pos = 0;
        } else if (c == '\b') {
            if (cmd_pos > 0) {
                cmd_pos--;
                screen_putchar('\b', 0x07);
            }
        } else if (cmd_pos < MAX_CMD - 1) {
            cmd_buffer[cmd_pos++] = c;
            screen_putchar(c, 0x07);
        }
    }
}