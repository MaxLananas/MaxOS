#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "mouse.h"
#include "idt.h"
#include "irq.h"
#include "exceptions.h"

void kmain(void) {
    screen_init();
    keyboard_init();
    timer_init(100);
    mouse_init();
    idt_init();
    irq_init();
    exceptions_init();

    screen_writeln("Kernel started", 0x0A);
    screen_writeln("Type something:", 0x0F);

    while (1);
}