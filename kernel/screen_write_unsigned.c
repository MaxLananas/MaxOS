#include "screen.h"

void screen_write_unsigned(unsigned int num) {
    char buffer[11];
    unsigned int i = 0;

    if (num == 0) {
        screen_putchar('0', 0x0F);
        return;
    }

    while (num > 0) {
        buffer[i++] = '0' + (num % 10);
        num /= 10;
    }

    while (i > 0) {
        screen_putchar(buffer[--i], 0x0F);
    }
}