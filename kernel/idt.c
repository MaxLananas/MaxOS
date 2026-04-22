#include "idt.h"
#include "io.h"

#define IDT_SIZE 256

struct IDTEntry {
    unsigned short base_low;
    unsigned short sel;
    unsigned char always0;
    unsigned char flags;
    unsigned short base_high;
} __attribute__((packed));

struct IDTPointer {
    unsigned short limit;
    unsigned int base;
} __attribute__((packed));

struct IDTEntry idt[IDT_SIZE];
struct IDTPointer idtp;

extern void idt_load();

void idt_set_gate(unsigned char num, unsigned int base, unsigned short sel, unsigned char flags) {
    idt[num].base_low = base & 0xFFFF;
    idt[num].base_high = (base >> 16) & 0xFFFF;
    idt[num].sel = sel;
    idt[num].always0 = 0;
    idt[num].flags = flags;
}

void idt_init(void) {
    idtp.limit = (sizeof(struct IDTEntry) * IDT_SIZE) - 1;
    idtp.base = (unsigned int)&idt;

    for (int i = 0; i < IDT_SIZE; i++) {
        idt_set_gate(i, 0, 0, 0);
    }

    idt_load();
}