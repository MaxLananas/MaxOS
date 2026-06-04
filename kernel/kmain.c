#include "kmain.h"
#include "screen.h"
#include "keyboard.h"
#include "mouse.h"
#include "idt.h"
#include "timer.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    idt_init();
    keyboard_init();
    mouse_init();
    timer_init(100);
    terminal_init();
    terminal_run();
}