#include "screen.h"
#include "keyboard.h"
#include "terminal.h"
#include "idt.h"
#include "isr.h"
#include "irq.h"
#include "timer.h"
#include "mouse.h"

void kmain(void) {
    screen_init();
    idt_init();
    isr_init();
    irq_init();
    timer_init(100);
    keyboard_init();
    mouse_init();
    terminal_init();

    screen_writeln("Kernel initialized", 0x0A);
    terminal_run();
}