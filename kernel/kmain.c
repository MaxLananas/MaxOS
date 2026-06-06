#include "kmain.h"
#include "screen.h"
#include "idt.h"
#include "irq.h"
#include "keyboard.h"
#include "mouse.h"
#include "timer.h"
#include "exceptions.h"

void kmain(void)
{
    screen_init();
    screen_writeln("Kernel started", 0x0A);
    screen_writeln("Initializing IDT...", 0x0F);
    idt_init();
    screen_writeln("IDT initialized", 0x0A);
    screen_writeln("Initializing exceptions...", 0x0F);
    exceptions_init();
    screen_writeln("Exceptions initialized", 0x0A);
    screen_writeln("Initializing IRQ...", 0x0F);
    irq_init();
    screen_writeln("IRQ initialized", 0x0A);
    screen_writeln("Initializing keyboard...", 0x0F);
    keyboard_init();
    screen_writeln("Keyboard initialized", 0x0A);
    screen_writeln("Initializing mouse...", 0x0F);
    mouse_init();
    screen_writeln("Mouse initialized", 0x0A);
    screen_writeln("Initializing timer...", 0x0F);
    timer_init(100);
    screen_writeln("Timer initialized", 0x0A);

    while (1) {
        asm volatile("hlt");
    }
}