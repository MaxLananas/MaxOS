#include "nmi_handler.h"
#include "screen.h"

void nmi_handler_init(void) {
    screen_writeln("NMI handler initialized", 0x0F);
}