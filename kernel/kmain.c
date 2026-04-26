#include "screen.h"
#include "keyboard.h"
#include "mouse.h"
#include "timer.h"
#include "idt.h"
#include "irq.h"

void kmain(void) {
    screen_init();
    screen_writeln("Kernel started", 0x0A);
    idt_init();
    irq_init();
    keyboard_init();
    mouse_init();
    timer_init(100);
    screen_writeln("IDT and IRQ initialized", 0x0A);
    while (1);
}