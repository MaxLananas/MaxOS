#include "isr.h"
#include "io.h"

void isr0() {
    fault_handler(0, 0);
}

void isr1() {
    fault_handler(1, 0);
}

void isr2() {
    fault_handler(2, 0);
}

void isr3() {
    fault_handler(3, 0);
}

void isr4() {
    fault_handler(4, 0);
}

void isr5() {
    fault_handler(5, 0);
}

void isr6() {
    fault_handler(6, 0);
}

void isr7() {
    fault_handler(7, 0);
}

void isr8() {
    unsigned int err_code;
    asm volatile("mov %%eax, %0" : "=r"(err_code));
    fault_handler(8, err_code);
}

void isr9() {
    fault_handler(9, 0);
}

void isr10() {
    unsigned int err_code;
    asm volatile("mov %%eax, %0" : "=r"(err_code));
    fault_handler(10, err_code);
}

void isr11() {
    fault_handler(11, 0);
}

void isr12() {
    unsigned int err_code;
    asm volatile("mov %%eax, %0" : "=r"(err_code));
    fault_handler(12, err_code);
}

void isr13() {
    unsigned int err_code;
    asm volatile("mov %%eax, %0" : "=r"(err_code));
    fault_handler(13, err_code);
}

void isr14() {
    unsigned int err_code;
    asm volatile("mov %%eax, %0" : "=r"(err_code));
    fault_handler(14, err_code);
}

void isr15() {
    fault_handler(15, 0);
}

void isr16() {
    fault_handler(16, 0);
}

void isr17() {
    unsigned int err_code;
    asm volatile("mov %%eax, %0" : "=r"(err_code));
    fault_handler(17, err_code);
}

void isr18() {
    fault_handler(18, 0);
}

void isr19() {
    fault_handler(19, 0);
}

void isr20() {
    fault_handler(20, 0);
}

void isr21() {
    fault_handler(21, 0);
}

void isr22() {
    fault_handler(22, 0);
}

void isr23() {
    fault_handler(23, 0);
}

void isr24() {
    fault_handler(24, 0);
}

void isr25() {
    fault_handler(25, 0);
}

void isr26() {
    fault_handler(26, 0);
}

void isr27() {
    fault_handler(27, 0);
}

void isr28() {
    fault_handler(28, 0);
}

void isr29() {
    fault_handler(29, 0);
}

void isr30() {
    fault_handler(30, 0);
}

void isr31() {
    fault_handler(31, 0);
}

void irq0() {
    outb(0x20, 0x20);
    outb(0xA0, 0x20);
}

void irq1() {
    outb(0x20, 0x20);
    outb(0xA0, 0x20);
    keyboard_handler();
}