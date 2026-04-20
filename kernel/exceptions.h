#ifndef EXCEPTIONS_H
#define EXCEPTIONS_H

void page_fault_handler(unsigned int err_code);
void double_fault_handler(unsigned int err_code);
void general_protection_fault_handler(unsigned int err_code);
void divide_error_handler();
void overflow_handler();
void bound_range_handler();
void invalid_opcode_handler();
void device_not_available_handler();
void invalid_tss_handler(unsigned int err_code);
void segment_not_present_handler(unsigned int err_code);
void stack_segment_fault_handler(unsigned int err_code);
void alignment_check_handler(unsigned int err_code);
void machine_check_handler();
void simd_fp_exception_handler();

#endif