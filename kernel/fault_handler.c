#include "kernel/fault_handler.h"
#include "drivers/screen.h"

static void itoa_hex(unsigned int n, char *buf) {
    int i;
    buf[0] = '0'; buf[1] = 'x';
    for (i = 9; i >= 2; i--) {
        unsigned int d = n & 0xF;
        buf[i] = (d < 10) ? ('0' + d) : ('A' + d - 10);
        n >>= 4;
    }
    buf[10] = 0;
}

void fault_handler(unsigned int num, unsigned int err) {
    char buf[11];
    screen_write("FAULT #", 0x0C);
    itoa_hex(num, buf);
    screen_write(buf, 0x0C);
    screen_write(" ERR=", 0x0C);
    itoa_hex(err, buf);
    screen_write(buf, 0x0C);
    screen_write("\n", 0x07);
    __asm__ volatile("cli; hlt");
}
