#include "kmain.h"
#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "idt.h"

void kmain(void) {
    screen_init();
    screen_clear();
    idt_init();
    keyboard_init();
    timer_init(100);
    screen_writeln("Kernel started", 0x0A);
    while (1) {
        asm volatile("hlt");
    }
}