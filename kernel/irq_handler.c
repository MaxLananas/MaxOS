#include "../kernel/io.h"
#include "../kernel/keyboard.h"
#include "../kernel/mouse.h"
#include "../kernel/timer.h"

void irq_handler(unsigned int num) {
    if (num == 33) {
        keyboard_handler();
    } else if (num == 44) {
        mouse_handler();
    } else if (num == 0) {
        timer_handler();
    }
}