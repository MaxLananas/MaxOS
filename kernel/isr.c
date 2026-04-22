#include "isr.h"
#include "idt.h"
#include "screen.h"
#include "io.h"

#define PIC1 0x20
#define PIC2 0xA0
#define PIC1_COMMAND PIC1
#define PIC1_DATA (PIC1+1)
#define PIC2_COMMAND PIC2
#define PIC2_DATA (PIC2+1)

#define ICW1_ICW4 0x01
#define ICW1_INIT 0x10
#define ICW4_8086 0x01

typedef struct {
    void (*handlers[256])(void);
} interrupt_handlers_t;

static interrupt_handlers_t interrupt_handlers;

void register_interrupt_handler(unsigned char n, void (*handler)(void)) {
    interrupt_handlers.handlers[n] = handler;
}

void isr_handler(unsigned int num, unsigned int err) {
    if (num < 32) {
        screen_writeln("Exception: ", 0x04);
        switch(num) {
            case 0: screen_writeln("Divide by zero", 0x04); break;
            case 1: screen_writeln("Debug", 0x04); break;
            case 2: screen_writeln("NMI", 0x04); break;
            case 3: screen_writeln("Breakpoint", 0x04); break;
            case 4: screen_writeln("Overflow", 0x04); break;
            case 5: screen_writeln("Bound range", 0x04); break;
            case 6: screen_writeln("Invalid opcode", 0x04); break;
            case 7: screen_writeln("Device not available", 0x04); break;
            case 8: screen_writeln("Double fault", 0x04); break;
            case 9: screen_writeln("Coprocessor segment overrun", 0x04); break;
            case 10: screen_writeln("Invalid TSS", 0x04); break;
            case 11: screen_writeln("Segment not present", 0x04); break;
            case 12: screen_writeln("Stack segment fault", 0x04); break;
            case 13: screen_writeln("General protection fault", 0x04); break;
            case 14: screen_writeln("Page fault", 0x04); break;
            case 15: screen_writeln("Reserved", 0x04); break;
            case 16: screen_writeln("x87 FPU error", 0x04); break;
            case 17: screen_writeln("Alignment check", 0x04); break;
            case 18: screen_writeln("Machine check", 0x04); break;
            case 19: screen_writeln("SIMD FPU exception", 0x04); break;
            case 20: screen_writeln("Virtualization exception", 0x04); break;
            case 21: screen_writeln("Control protection exception", 0x04); break;
            default: screen_writeln("Unknown exception", 0x04); break;
        }

        while(1);
    } else {
        if (interrupt_handlers.handlers[num] != 0) {
            interrupt_handlers.handlers[num]();
        }

        if (num >= 40) {
            outb(0xA0, 0x20);
        }
        outb(0x20, 0x20);
    }
}

void irq_handler(unsigned int num) {
    if (num >= 40) {
        outb(0xA0, 0x20);
    }
    outb(0x20, 0x20);
}