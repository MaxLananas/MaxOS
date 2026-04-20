#include "exceptions.h"
#include "io.h"
#include "screen.h"

void page_fault_handler(unsigned int err_code) {
    unsigned int fault_addr;
    asm volatile("mov %%cr2, %0" : "=r"(fault_addr));

    screen_write("Page Fault at address: ");
    screen_write_hex(fault_addr);
    screen_write(" (Error code: ");
    screen_write_hex(err_code);
    screen_write(")\n");

    if (err_code & 0x1) {
        screen_write(" - Page protection violation\n");
    } else {
        screen_write(" - Non-present page\n");
    }

    if (err_code & 0x2) {
        screen_write(" - Write operation\n");
    } else {
        screen_write(" - Read operation\n");
    }

    if (err_code & 0x4) {
        screen_write(" - User mode\n");
    } else {
        screen_write(" - Supervisor mode\n");
    }

    screen_write("System halted.\n");
    asm volatile("cli; hlt");
}

void double_fault_handler(unsigned int err_code) {
    screen_write("Double Fault (Error code: ");
    screen_write_hex(err_code);
    screen_write(")\nSystem halted.\n");
    asm volatile("cli; hlt");
}

void general_protection_fault_handler(unsigned int err_code) {
    screen_write("General Protection Fault (Error code: ");
    screen_write_hex(err_code);
    screen_write(")\nSystem halted.\n");
    asm volatile("cli; hlt");
}

void divide_error_handler() {
    screen_write("Divide Error\nSystem halted.\n");
    asm volatile("cli; hlt");
}

void overflow_handler() {
    screen_write("Overflow\nSystem halted.\n");
    asm volatile("cli; hlt");
}

void bound_range_handler() {
    screen_write("Bound Range Exceeded\nSystem halted.\n");
    asm volatile("cli; hlt");
}

void invalid_opcode_handler() {
    screen_write("Invalid Opcode\nSystem halted.\n");
    asm volatile("cli; hlt");
}

void device_not_available_handler() {
    screen_write("Device Not Available\nSystem halted.\n");
    asm volatile("cli; hlt");
}

void invalid_tss_handler(unsigned int err_code) {
    screen_write("Invalid TSS (Error code: ");
    screen_write_hex(err_code);
    screen_write(")\nSystem halted.\n");
    asm volatile("cli; hlt");
}

void segment_not_present_handler(unsigned int err_code) {
    screen_write("Segment Not Present (Error code: ");
    screen_write_hex(err_code);
    screen_write(")\nSystem halted.\n");
    asm volatile("cli; hlt");
}

void stack_segment_fault_handler(unsigned int err_code) {
    screen_write("Stack Segment Fault (Error code: ");
    screen_write_hex(err_code);
    screen_write(")\nSystem halted.\n");
    asm volatile("cli; hlt");
}

void alignment_check_handler(unsigned int err_code) {
    screen_write("Alignment Check (Error code: ");
    screen_write_hex(err_code);
    screen_write(")\nSystem halted.\n");
    asm volatile("cli; hlt");
}

void machine_check_handler() {
    screen_write("Machine Check\nSystem halted.\n");
    asm volatile("cli; hlt");
}

void simd_fp_exception_handler() {
    screen_write("SIMD Floating-Point Exception\nSystem halted.\n");
    asm volatile("cli; hlt");
}