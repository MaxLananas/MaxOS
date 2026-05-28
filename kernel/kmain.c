#include "screen.h"
#include "keyboard.h"
#include "mouse.h"
#include "timer.h"
#include "idt.h"
#include "irq.h"
#include "fault_handler.h"

void kmain(void) {
    screen_init();
    idt_init();
    irq_init();
    keyboard_init();
    mouse_init();
    timer_init(100);

    screen_writeln("Kernel initialized", 0x0A);
    screen_writeln("Welcome to Bare Metal OS", 0x0F);

    for (;;);
}