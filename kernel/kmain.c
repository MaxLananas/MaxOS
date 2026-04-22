#include "drivers/screen.h"
#include "kernel/keyboard.h"
#include "kernel/idt.h"
#include "kernel/timer.h"

void kmain(void) {
    screen_init();
    idt_init();
    keyboard_init();
    timer_init(100);
    screen_writeln("Kernel started", 0x0A);
    for(;;);
}