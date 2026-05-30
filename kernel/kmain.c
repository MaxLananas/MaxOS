#include "kmain.h"
#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "timer.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x0A);

    idt_init();
    keyboard_init();
    timer_init(100);

    screen_writeln("IDT initialized", 0x0A);
    screen_writeln("Keyboard initialized", 0x0A);
    screen_writeln("Timer initialized", 0x0A);

    for (;;);
}