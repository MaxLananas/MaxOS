#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "idt.h"
#include "irq.h"
#include "exceptions.h"

void kmain(void) {
    screen_init();
    idt_init();
    exceptions_init();
    irq_init();
    keyboard_init();
    timer_init(100);

    screen_writeln("Kernel initialized", 0x0A);
    for(;;);
}