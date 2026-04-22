#include "kernel/isr.h"
#include "kernel/io.h"
#include "drivers/screen.h"

static const char *exception_messages[] = {
    "Division By Zero", "Debug", "Non Maskable Interrupt",
    "Breakpoint", "Into Detected Overflow", "Out of Bounds",
    "Invalid Opcode", "No Coprocessor", "Double Fault",
    "Coprocessor Segment Overrun", "Bad TSS", "Segment Not Present",
    "Stack Fault", "General Protection Fault", "Page Fault",
    "Unknown Interrupt", "Coprocessor Fault", "Alignment Check",
    "Machine Check", "Reserved", "Reserved", "Reserved",
    "Reserved", "Reserved", "Reserved", "Reserved",
    "Reserved", "Reserved", "Reserved", "Reserved",
    "Reserved", "Reserved"
};

void isr_handler(struct registers *regs) {
    if (regs->int_no < 32) {
        screen_write("EXCEPTION: ", 0x0C);
        screen_write(exception_messages[regs->int_no], 0x0C);
        screen_write("\n", 0x07);
        __asm__ volatile("cli; hlt");
    }
}

void irq_handler(struct registers *regs) {
    if (regs->int_no >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}
