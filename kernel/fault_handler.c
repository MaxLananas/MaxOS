#include "screen.h"
#include "io.h"

void fault_handler(unsigned int num, unsigned int err) {
    screen_writeln("Exception:", 0x0F);
    screen_putchar('0' + num / 10, 0x0F);
    screen_putchar('0' + num % 10, 0x0F);
    screen_putchar('\n', 0x0F);

    if (err != 0) {
        screen_writeln("Error code:", 0x0F);
        screen_putchar('0' + err / 10, 0x0F);
        screen_putchar('0' + err % 10, 0x0F);
        screen_putchar('\n', 0x0F);
    }

    for (;;);
}