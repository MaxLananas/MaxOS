#include "screen.h"

void screen_write_hex(unsigned int num) {
    char buffer[9];
    unsigned int i = 0;

    if (num == 0) {
        screen_write("00000000", 0x0F);
        return;
    }

    while (num > 0) {
        unsigned int digit = num % 16;
        buffer[i++] = (digit < 10) ? ('0' + digit) : ('a' + digit - 10);
        num /= 16;
    }

    while (i < 8) {
        buffer[i++] = '0';
    }

    while (i > 0) {
        screen_putchar(buffer[--i], 0x0F);
    }
}