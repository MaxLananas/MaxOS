#include "keyboard.h"
#include "io.h"
#include "idt.h"
#include "screen.h"

#define KEYBOARD_DATA_PORT 0x60
#define KEYBOARD_STATUS_PORT 0x64

static char key_buffer[256];
static unsigned int key_count = 0;

void keyboard_callback() {
    unsigned char scancode = inb(KEYBOARD_DATA_PORT);
    if (scancode < 128) {
        key_buffer[key_count++] = scancode;
    }
}

void keyboard_init(void) {
    idt_set_gate(33, (unsigned int)isr33, 0x08, 0x8E);
}

char keyboard_getchar(void) {
    while (key_count == 0)
        asm volatile("hlt");
    char c = key_buffer[0];
    for (unsigned int i = 0; i < key_count - 1; i++) {
        key_buffer[i] = key_buffer[i + 1];
    }
    key_count--;
    return c;
}