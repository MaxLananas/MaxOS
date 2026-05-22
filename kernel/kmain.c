#include "kmain.h"
#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "idt.h"
#include "mouse.h"
#include "fault_handler.h"

void kmain(void) {
    screen_init();
    idt_init();
    keyboard_init();
    timer_init(100);
    mouse_init();

    screen_writeln("Kernel initialized", 0x0A);

    while (1) {
        __asm__("hlt");
    }
}