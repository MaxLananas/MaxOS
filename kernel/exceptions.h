#ifndef EXCEPTIONS_H
#define EXCEPTIONS_H

void exceptions_init(void);
void divide_error(void);
void debug_exception(void);
void nmi_interrupt(void);
void breakpoint_exception(void);
void overflow_exception(void);
void bound_range_exceeded(void);
void invalid_opcode(void);
void device_not_available(void);
void double_fault_exception(void);
void coprocessor_segment_overrun(void);
void invalid_tss_exception(void);
void segment_not_present(void);
void stack_segment_fault(void);
void general_protection_fault(void);
void page_fault(void);
void x87_fpu_error(void);
void alignment_check(void);
void machine_check(void);
void simd_fpu_exception(void);

#endif