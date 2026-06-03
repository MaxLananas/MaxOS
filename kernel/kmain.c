#include "kmain.h"
#include "screen.h"
#include "idt.h"
#include "irq.h"
#include "timer.h"
#include "keyboard.h"
#include "mouse.h"
#include "exceptions.h"
#include "fault_handler.h"
#include "mem.h"
#include "paging.h"
#include "heap.h"
#include "ata.h"
#include "terminal.h"
#include "devfs.h"
#include "vfs.h"

void kmain(void) {
    screen_init();
    idt_init();
    irq_init();
    exceptions_init();
    keyboard_init();
    mouse_init();
    timer_init(100);
    mem_init(1024);
    paging_init();
    heap_init((void *)0x100000, 1024 * 1024);
    ata_init();
    devfs_init();
    vfs_init();
    terminal_init();
    terminal_run();

    while (1);
}