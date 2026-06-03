#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "timer.h"
#include "mouse.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_set_color(0x0F);
    screen_writeln("Kernel started successfully", 0x0A);

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