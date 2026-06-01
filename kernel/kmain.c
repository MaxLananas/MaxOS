#include "kmain.h"
#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "mouse.h"
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
    mouse_init();

    screen_writeln("Kernel initialized", 0x0A);
    screen_writeln("Welcome to Bare Metal OS", 0x0F);

    for (;;);
}