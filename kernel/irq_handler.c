#include "io.h"
#include "timer.h"
#include "irq.h"

void irq_handler(unsigned int num) {
    if (num >= 0 && num < 16) {
        if (num == 0) {
            timer_handler();
        }
        irq_install_handler(num);
    }
}