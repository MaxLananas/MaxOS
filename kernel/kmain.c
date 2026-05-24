#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "idt.h"
#include "fault_handler.h"
#include "mouse.h"

void kmain(void) {
    screen_init();
    idt_init();
    keyboard_init();
    timer_init(100);
    mouse_init();

    screen_writeln("Kernel started", 0x0A);
    screen_writeln("Type something:", 0x0F);

    while (1);
}