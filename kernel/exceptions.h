#ifndef EXCEPTIONS_H
#define EXCEPTIONS_H

void page_fault_handler(unsigned int fault_addr, unsigned int err_code);
void double_fault_handler(unsigned int err_code);
void nmi_handler();
void machine_check_handler();
void general_protection_fault_handler(unsigned int err_code);

#endif