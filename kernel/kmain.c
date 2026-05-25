#include "kmain.h"
#include "screen.h"
#include "idt.h"
#include "timer.h"
#include "keyboard.h"
#include "fault_handler.h"
#include "mouse.h"

void kmain() {
    screen_init();
    idt_init();
    timer_init(100);
    keyboard_init();
    mouse_init();
    fault_handler_init();

    screen_writeln("Kernel started successfully", 0x0A);
    while (1);
}