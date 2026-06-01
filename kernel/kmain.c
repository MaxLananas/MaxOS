#include "kmain.h"
#include "screen.h"
#include "keyboard.h"
#include "mouse.h"
#include "timer.h"
#include "idt.h"
#include "irq.h"
#include "exceptions.h"
#include "ata.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    idt_init();
    irq_init();
    exceptions_init();
    keyboard_init();
    mouse_init();
    timer_init(100);
    ata_init();

    screen_writeln("Kernel initialized", 0x0A);
    terminal_init();
    terminal_run();
}