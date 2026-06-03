#include "keyboard.h"
#include "io.h"
#include "irq.h"
#include "screen.h"

static char keyboard_buffer[256];
static unsigned int buffer_pos = 0;

void keyboard_init(void)
{
    outb(0x64, 0xAE);
    outb(0x64, 0x20);
}

void keyboard_handler(void)
{
    unsigned char scancode = inb(0x60);
    keyboard_buffer[buffer_pos++] = scancode;
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