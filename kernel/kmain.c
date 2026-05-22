#include "kmain.h"
#include "terminal.h"

void kmain() {
    terminal_init();
    terminal_run();
    for (;;);
}