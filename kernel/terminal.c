#include "terminal.h"
#include "screen.h"
#include "keyboard.h"
#include "pmm.h"

void terminal_init(void) {
}

void terminal_run(void) {
    screen_writeln("Terminal ready", 0x0F);
}

void terminal_process(const char *cmd) {
    unsigned int used = mem_used_pages();
    unsigned int total = mem_total_pages();

    screen_writeln("Memory usage:", 0x0A);
    screen_putchar(' ', 0x0F);
    screen_write("Used: ", 0x0F);
    screen_putchar('0' + (used / 1000), 0x0F);
    screen_putchar('0' + ((used / 100) % 10), 0x0F);
    screen_putchar('0' + ((used / 10) % 10), 0x0F);
    screen_putchar('0' + (used % 10), 0x0F);
    screen_putchar('/', 0x0F);
    screen_putchar(' ', 0x0F);
    screen_write("Total: ", 0x0F);
    screen_putchar('0' + (total / 1000), 0x0F);
    screen_putchar('0' + ((total / 100) % 10), 0x0F);
    screen_putchar('0' + ((total / 10) % 10), 0x0F);
    screen_putchar('0' + (total % 10), 0x0F);
    screen_putchar('\n', 0x0F);
}