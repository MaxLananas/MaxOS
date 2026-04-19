#include "drivers/screen.h"
#include "drivers/keyboard.h"
#include "kernel/memory.h"
#include "kernel/idt.h"
#include "tests/unit_tests.h"

void test_screen(void) {
    v_init();
    v_put(0, 0, 'A', 0x0F, C_BLACK);
    v_str(1, 0, "Test screen", 0x0F, C_BLACK);
    v_fill(0, 1, 80, 25, 0x0F, C_BLACK);
}

void test_keyboard(void) {
    kb_init();
    if (kb_haskey()) {
        char c = kb_getchar();
        v_str(0, 0, "Key pressed: ", 0x0F, C_BLACK);
        v_put(13, 0, c, 0x0F, C_BLACK);
    }
}

void test_memory(void) {
    unsigned int test_addr = 0x1000;
    memory_set(test_addr, 0xAA, 10);
    unsigned char* ptr = (unsigned char*)test_addr;
    for (int i = 0; i < 10; i++) {
        if (ptr[i] != 0xAA) {
            v_str(0, 0, "Memory test failed", 0x0F, C_BLACK);
            return;
        }
    }
    v_str(0, 0, "Memory test passed", 0x0F, C_BLACK);
}

void test_idt(void) {
    idt_init();
    v_str(0, 0, "IDT initialized", 0x0F, C_BLACK);
}

void run_all_tests(void) {
    test_screen();
    test_keyboard();
    test_memory();
    test_idt();
}