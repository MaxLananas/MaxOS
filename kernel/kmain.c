#include "screen.h"
#include "keyboard.h"
#include "idt.h"
#include "timer.h"
#include "fault_handler.h"

void kmain(void) {
    screen_init();
    idt_init();
    keyboard_init();
    timer_init(100);
    screen_writeln("Kernel initialized", 0x0F);
    for(;;);
}