#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "timer.h"
#include "mouse.h"
#include "ata.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x0A);

    idt_init();
    exceptions_init();
    irq_init();
    timer_init(100);
    keyboard_init();
    mouse_init();

    screen_writeln("All systems initialized", 0x0A);

    for (;;);
}