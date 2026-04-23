#include "drivers/screen.h"
#include "kernel/keyboard.h"
#include "kernel/idt.h"
#include "kernel/timer.h"
#include "kernel/memory.h"

void kmain(void) {
    screen_init();
    idt_init();
    keyboard_init();
    timer_init(100);
    mem_init(16384);
    screen_writeln("Kernel started with paging", 0x0A);
    for(;;);
}