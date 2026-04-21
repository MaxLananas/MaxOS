#include "mouse.h"
#include "screen.h"

void mouse_draw_cursor() {
    static int old_x = 0;
    static int old_y = 0;
    static int first_call = 1;

    if (!first_call) {
        screen_putchar(' ', 0x0F);
        screen_putchar(' ', 0x0F);
    }

    screen_putchar(0xDB, 0x0F);
    screen_putchar(0xDB, 0x0F);

    first_call = 0;
}