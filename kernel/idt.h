#ifndef IDT_H
#define IDT_H

struct registers {
    unsigned int edi, esi, ebp, esp_dummy, ebx, edx, ecx, eax;
    unsigned int int_no, err_code;
    unsigned int eip, cs, eflags, useresp, ss;
};

void idt_init(void);
void register_interrupt_handler(unsigned char n, void (*handler)(struct registers* regs));

#endif