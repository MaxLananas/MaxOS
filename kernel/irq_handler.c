#include "irq_handler.h"
#include "io.h"

extern void timer_handler(void);

void irq_handler(unsigned int num) {
    if (num >= 32 && num < 48) {
        timer_handler();
    }
}