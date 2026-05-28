#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "mouse.h"
#include "idt.h"
#include "exceptions.h"

void kmain() {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x0A);

    idt_init();
    keyboard_init();
    timer_init(100);
    mouse_init();

    screen_writeln("IDT initialized", 0x0A);
    screen_writeln("Keyboard initialized", 0x0A);
    screen_writeln("Timer initialized", 0x0A);
    screen_writeln("Mouse initialized", 0x0A);

    for(;;);
}