#include "kmain.h"
#include "screen.h"
#include "idt.h"
#include "timer.h"
#include "keyboard.h"
#include "mouse.h"
#include "exceptions.h"

void kmain(void)
{
    screen_init();
    idt_init();
    timer_init(100);
    keyboard_init();
    mouse_init();
    exceptions_init();

    screen_writeln("Kernel started", 0x0A);
    screen_writeln("Welcome to Bare Metal OS", 0x0F);

    while (1) {
        asm volatile("hlt");
    }
}