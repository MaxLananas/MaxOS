#include "kmain.h"
#include "screen.h"
#include "keyboard.h"
#include "timer.h"
#include "idt.h"
#include "irq.h"
#include "exceptions.h"
#include "fault_handler.h"
#include "mem.h"
#include "paging.h"
#include "heap.h"
#include "ata.h"
#include "terminal.h"
#include "mouse.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started!", 0x0A);

    idt_init();
    exceptions_init();
    irq_init();
    timer_init(100);
    keyboard_init();
    mouse_init();
    mem_init(1024 * 1024);
    paging_init();
    heap_init((void*)0xC0000000, 1024 * 1024);
    ata_init();
    terminal_init();

    screen_writeln("All systems initialized!", 0x0A);
    terminal_run();
}