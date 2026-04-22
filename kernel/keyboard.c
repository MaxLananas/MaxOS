#include "drivers/keyboard.h"
#include "kernel/idt.h"
#include "kernel/io.h"
#include "kernel/isr.h"

#define KEYBOARD_BUF_SIZE 256

static char kb_buf[KEYBOARD_BUF_SIZE];
static int  kb_head = 0;
static int  kb_tail = 0;

static const char sc_ascii[] = {
    0, 0, '1','2','3','4','5','6','7','8','9','0','-','=','\b',
    '\t','q','w','e','r','t','y','u','i','o','p','[',']','\n',
    0,'a','s','d','f','g','h','j','k','l',';','\'','`',
    0,'\\','z','x','c','v','b','n','m',',','.','/',0,'*',
    0,' '
};

static const char sc_ascii_shift[] = {
    0, 0, '!','@','#','$','%','^','&','*','(',')','_','+','\b',
    '\t','Q','W','E','R','T','Y','U','I','O','P','{','}','\n',
    0,'A','S','D','F','G','H','J','K','L',':','"','~',
    0,'|','Z','X','C','V','B','N','M','<','>','?',0,'*',
    0,' '
};

static int shift_held = 0;

static void keyboard_callback(struct registers *regs) {
    unsigned char sc;
    char c;
    (void)regs;
    sc = inb(0x60);
    if (sc == 0x2A || sc == 0x36) { shift_held = 1; return; }
    if (sc == 0xAA || sc == 0xB6) { shift_held = 0; return; }
    if (sc & 0x80) return;
    if (sc < sizeof(sc_ascii)) {
        c = shift_held ? sc_ascii_shift[sc] : sc_ascii[sc];
        if (c) {
            int next = (kb_head + 1) % KEYBOARD_BUF_SIZE;
            if (next != kb_tail) {
                kb_buf[kb_head] = c;
                kb_head = next;
            }
        }
    }
}

void keyboard_init(void) {
    idt_set_gate(33, (unsigned int)isr33, 0x08, 0x8E);
    outb(0x21, inb(0x21) & ~0x02);
}

char keyboard_getchar(void) {
    char c;
    while (kb_head == kb_tail) {
        __asm__ volatile("hlt");
    }
    c = kb_buf[kb_tail];
    kb_tail = (kb_tail + 1) % KEYBOARD_BUF_SIZE;
    return c;
}

int keyboard_has_input(void) {
    return kb_head != kb_tail;
}
