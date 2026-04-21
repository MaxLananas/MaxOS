#include "exceptions.h"
#include "fault_handler.h"
#include "screen.h"

void exceptions_init() {
    screen_writeln("Exceptions initialized", 0x0F);
}

void exception_handler(unsigned int num, unsigned int err) {
    screen_set_color(0x0C);
    screen_writeln("EXCEPTION: ", 0x0F);
    screen_putchar('0' + num / 10, 0x0C);
    screen_putchar('0' + num % 10, 0x0C);
    screen_writeln("", 0x0F);
    fault_handler(num, err);
}