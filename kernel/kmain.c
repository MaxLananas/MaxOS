#include "drivers/screen.h"
#include "kernel/terminal.h"

void kmain(void) {
    terminal_init();
    terminal_run();
}