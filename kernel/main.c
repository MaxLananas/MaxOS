#include "screen.h"
#include "idt.h"
#include "timer.h"
#include "keyboard.h"
#include "terminal.h"
#include "fs/vfs.h"

void kmain(void) {
    screen_init();
    idt_init();
    timer_init(1000);
    keyboard_init();
    terminal_init();
    vfs_init();
    terminal_run();
}