#ifndef TIMER_H
#define TIMER_H

struct regs {
    unsigned int gs, fs, es, ds;
    unsigned int edi, esi, ebp, esp, ebx, edx, ecx, eax;
    unsigned int int_no, err_code;
    unsigned int eip, cs, eflags, useresp, ss;
};

void timer_init(unsigned int hz);
unsigned int timer_get_ticks(void);
void timer_sleep(unsigned int ms);
void timer_callback(struct regs *r);

#endif