#include "screen.h"
#include "timer.h"
#include "keyboard.h"
#include "idt.h"
#include "io.h"
#include "mouse.h"
#include "mouse_handler.h"

void kmain(void) {
    screen_init();
    screen_clear();
    screen_set_color(0x0F);
    screen_writeln("Kernel initialized", 0x0F);

    idt_init();
    timer_init(1000);
    keyboard_init();
    mouse_init();

    asm volatile("sti");

    while (1) {
        mouse_draw_cursor();
        asm volatile("hlt");
    }
}