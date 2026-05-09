#include "kmain.h"
#include "screen.h"
#include "keyboard.h"
#include "terminal.h"
#include "idt.h"
#include "timer.h"
#include "mouse.h"
#include "paging.h"

void kmain(void) {
    screen_init();
    idt_init();
    timer_init(100);
    keyboard_init();
    mouse_init();
    paging_init();

    screen_writeln("Kernel started", 0x0A);
    terminal_run();

    for (;;);
}