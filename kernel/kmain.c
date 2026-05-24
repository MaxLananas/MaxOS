#include "kmain.h"
#include "screen.h"
#include "idt.h"
#include "timer.h"
#include "keyboard.h"
#include "mouse.h"
#include "fault_handler.h"

void kmain(void) {
    screen_init();
    idt_init();
    timer_init(100);
    keyboard_init();
    mouse_init();
    screen_writeln("Kernel initialized", 0x0A);
    while (1);
}