#include "isr.h"
#include "io.h"
#include "screen.h"

void isr_handler(unsigned int num, unsigned int err) {
    if (num == 32) {
        timer_callback();
    } else {
        screen_write("ISR: ", 0x0F);
        char num_str[4];
        num_str[0] = '0' + num / 100;
        num_str[1] = '0' + (num / 10) % 10;
        num_str[2] = '0' + num % 10;
        num_str[3] = 0;
        screen_writeln(num_str, 0x0F);
    }
}