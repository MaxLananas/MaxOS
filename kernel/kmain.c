#include "screen.h"
#include "idt.h"
#include "isr.h"
#include "irq.h"
#include "timer.h"
#include "keyboard.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Booting...", 0x0F);

    idt_init();
    isr_install();
    irq_install();
    timer_init(1000);
    keyboard_init();

    __asm__ volatile ("sti");

    while (1) {
        __asm__ volatile ("hlt");
    }
}