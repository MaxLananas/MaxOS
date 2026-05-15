#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "timer.h"
#include "fault_handler.h"

void kmain(void) {
    screen_init();
    idt_init();
    timer_init(100);
    keyboard_init();

    screen_writeln("Kernel started", 0x0A);
    for (;;);
}