#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "idt.h"
#include "isr.h"
#include "irq.h"
#include "fault_handler.h"

void kmain(void) {
    screen_init();
    screen_clear();

    idt_init();
    isr_install();
    irq_install();
    keyboard_init();
    timer_init(100);

    screen_write("Kernel initialized successfully\n", 0x0A);
    screen_writeln("Type commands below:", 0x0F);

    terminal_init();
    terminal_run();
}