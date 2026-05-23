#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "mouse.h"
#include "idt.h"
#include "io.h"

void kmain(void)
{
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x0A);

    idt_init();
    keyboard_init();
    timer_init(100);
    mouse_init();

    screen_writeln("Initialization complete", 0x0A);
    screen_writeln("Ready", 0x0F);

    for (;;) {
        asm volatile("hlt");
    }
}