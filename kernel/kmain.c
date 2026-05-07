#include "screen.h"
#include "keyboard.h"
#include "terminal.h"
#include "idt.h"
#include "irq.h"
#include "timer.h"
#include "fault_handler.h"
#include "ata.h"
#include "fs/vfs.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_writeln("Kernel started", 0x02);

    idt_init();
    irq_init();
    irq_handler_init();
    timer_init(100);
    ata_init();
    vfs_init();
    terminal_init();

    screen_writeln("All systems initialized", 0x02);
    terminal_run();
}