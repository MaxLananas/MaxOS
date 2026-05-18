#ifndef IDT_LOAD_H
#define IDT_LOAD_H

struct IDTPtr;

void idt_load(struct IDTPtr *idt_ptr);

#endif