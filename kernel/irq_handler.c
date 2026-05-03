#include "irq.h"
#include "timer.h"
#include "keyboard.h"

void irq_handler(unsigned int num) {
    if (num == 32) {
        timer_handler();
    } else if (num == 33) {
        keyboard_handler();
    }
}