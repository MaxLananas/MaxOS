#include "irq.h"
#include "io.h"
#include "idt.h"

#define PIC1 0x20
#define PIC2 0xA0
#define PIC1_COMMAND PIC1
#define PIC1_DATA (PIC1 + 1)
#define PIC2_COMMAND PIC2
#define PIC2_DATA (PIC2 + 1)

#define ICW1_ICW4 0x01
#define ICW1_INIT 0x10
#define ICW4_8086 0x01

void irq_set_handler(unsigned char irq, void (*handler)(void)) {
    idt_set_gate(32 + irq, (unsigned int)handler, 0x08, 0x8E);
}

void irq_init(void) {
    outb(PIC1_COMMAND, ICW1_INIT + ICW1_ICW4);
    outb(PIC2_COMMAND, ICW1_INIT + ICW1_ICW4);
    outb(PIC1_DATA, 0x20);
    outb(PIC2_DATA, 0x28);
    outb(PIC1_DATA, 0x04);
    outb(PIC2_DATA, 0x02);
    outb(PIC1_DATA, ICW4_8086);
    outb(PIC2_DATA, ICW4_8086);
}