#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "idt.h"
#include "irq.h"
#include "fault_handler.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x0A);

    idt_init();
    irq_init();
    keyboard_init();
    timer_init(100);

    screen_writeln("IDT and IRQ initialized", 0x0A);
    screen_writeln("Keyboard and timer initialized", 0x0A);

    for (;;) {
        char c = keyboard_getchar();
        if (c != 0) {
            screen_putchar(c, 0x0F);
        }
    }
}