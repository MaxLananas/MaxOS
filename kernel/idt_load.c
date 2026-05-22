#include "idt.h"

void idt_load(struct IDTPtr *idt_ptr) {
    asm volatile("lidt %0" : : "m"(*idt_ptr));
}