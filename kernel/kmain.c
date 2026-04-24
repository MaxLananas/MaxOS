#include "screen.h"
#include "keyboard.h"
#include "mouse.h"
#include "timer.h"
#include "idt.h"
#include "irq.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x0A);

    idt_init();
    irq_install_handler(0, timer_handler);
    irq_install_handler(1, keyboard_handler);
    irq_install_handler(12, mouse_handler);

    keyboard_init();
    mouse_init();
    timer_init(100);

    screen_writeln("IDT and IRQ initialized", 0x0A);

    while (1) {
        __asm__ volatile("hlt");
    }
}