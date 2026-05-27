#ifndef SYSCALL_H
#define SYSCALL_H

#include "regs.h"

void syscall_init(void);
void syscall_handler(unsigned int eax, unsigned int ebx, unsigned int ecx, unsigned int edx);

#endif