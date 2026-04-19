#include "keyboard.h"
#include "screen.h"

void kmain(void) {
    v_init();
    kb_init();
    v_str(0, 0, "Kernel started", 15, 0);
    while(1);
}