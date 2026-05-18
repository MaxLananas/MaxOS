#include "keyboard.h"
#include "io.h"
#include "screen.h"
#include "irq.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

static char keyboard_buffer[256];
static unsigned int buffer_pos = 0;

void keyboard_init(void) {
    register_interrupt_handler(33, keyboard_handler);
}

char keyboard_getchar(void) {
    if (buffer_pos == 0) return 0;
    char c = keyboard_buffer[0];
    for (unsigned int i = 0; i < buffer_pos - 1; i++) {
        keyboard_buffer[i] = keyboard_buffer[i + 1];
    }
    buffer_pos--;
    return c;
}

void keyboard_handler(void) {
    unsigned char scancode = inb(KEYBOARD_DATA_PORT);
    if (scancode & 0x80) return;

    keyboard_buffer[buffer_pos++] = scancode;
    if (buffer_pos >= 256) buffer_pos = 0;
}
```=== END FILE ===