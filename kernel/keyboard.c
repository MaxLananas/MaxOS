#include "keyboard.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

static char keyboard_buffer[256];
static unsigned int buffer_pos = 0;

void keyboard_callback(void)
{
    unsigned char scancode = inb(0x60);

    if (scancode & 0x80) {
        scancode -= 0x80;
        if (scancode == 14) {
            if (buffer_pos > 0) {
                buffer_pos--;
                screen_putchar('\b', 0x0F);
            }
        }
    } else {
        keyboard_buffer[buffer_pos++] = scancode;
        screen_putchar(scancode, 0x0F);
    }
}

void keyboard_init(void)
{
    irq_install_handler(1, keyboard_callback);
}

char keyboard_getchar(void)
{
    if (buffer_pos == 0) return 0;
    char c = keyboard_buffer[0];
    for (unsigned int i = 0; i < buffer_pos - 1; i++) {
        keyboard_buffer[i] = keyboard_buffer[i + 1];
    }
    buffer_pos--;
    return c;
}