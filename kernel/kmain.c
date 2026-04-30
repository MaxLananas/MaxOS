#include "terminal.h"

void kmain(void) {
    terminal_init();
    terminal_run();
    for(;;);
}