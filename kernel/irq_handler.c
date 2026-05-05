#include "irq.h"
#include "screen.h"
#include "keyboard.h"
#include "mouse.h"
#include "timer.h"

void irq_handler(unsigned int num) {
    if (num >= 32 && num <= 47) {
        if (num == 33) {
            keyboard_handler();
        } else if (num == 44) {
            mouse_handler();
        }
        timer_handler(num);
    }
}