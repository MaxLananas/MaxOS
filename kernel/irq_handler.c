#include "irq.h"
#include "keyboard.h"
#include "timer.h"
#include "mouse.h"

void irq_handler(unsigned int num) {
    if (num == 32) {
        timer_handler();
    } else if (num == 33) {
        keyboard_handler();
    } else if (num == 44) {
        mouse_handler();
    }
}