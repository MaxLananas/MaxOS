#include "kmain.h"
#include "screen.h"
#include "terminal.h"

void kmain(void) {
    screen_init();
    terminal_init();
    terminal_run();
}