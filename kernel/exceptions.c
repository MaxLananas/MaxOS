#include "exceptions.h"
#include "fault_handler.h"
#include "screen.h"

void exceptions_init(void)
{
    screen_writeln("Exceptions initialized", 0x0F);
}

void divide_error(void)
{
    screen_writeln("Divide Error", 0x0C);
    fault_handler(0, 0);
}

void debug_exception(void)
{
    screen_writeln("Debug Exception", 0x0C);
    fault_handler(1, 0);
}

void nmi_interrupt(void)
{
    screen_writeln("NMI Interrupt", 0x0C);
    fault_handler(2, 0);
}

void breakpoint_exception(void)
{
    screen_writeln("Breakpoint Exception", 0x0C);
    fault_handler(3, 0);
}

void overflow_exception(void)
{
    screen_writeln("Overflow Exception", 0x0C);
    fault_handler(4, 0);
}

void bound_range_exceeded(void)
{
    screen_writeln("Bound Range Exceeded", 0x0C);
    fault_handler(5, 0);
}

void invalid_opcode(void)
{
    screen_writeln("Invalid Opcode", 0x0C);
    fault_handler(6, 0);
}

void device_not_available(void)
{
    screen_writeln("Device Not Available", 0x0C);
    fault_handler(7, 0);
}

void double_fault_exception(void)
{
    screen_writeln("Double Fault Exception", 0x0C);
    fault_handler(8, 0);
}

void coprocessor_segment_overrun(void)
{
    screen_writeln("Coprocessor Segment Overrun", 0x0C);
    fault_handler(9, 0);
}

void invalid_tss_exception(void)
{
    screen_writeln("Invalid TSS Exception", 0x0C);
    fault_handler(10, 0);
}

void segment_not_present(void)
{
    screen_writeln("Segment Not Present", 0x0C);
    fault_handler(11, 0);
}

void stack_segment_fault(void)
{
    screen_writeln("Stack Segment Fault", 0x0C);
    fault_handler(12, 0);
}

void general_protection_fault(void)
{
    screen_writeln("General Protection Fault", 0x0C);
    fault_handler(13, 0);
}

void page_fault(void)
{
    unsigned int fault_addr;
    asm volatile("mov %%cr2, %0" : "=r" (fault_addr));
    screen_writeln("Page Fault", 0x0C);
    fault_handler(14, fault_addr);
}

void x87_fpu_error(void)
{
    screen_writeln("x87 FPU Error", 0x0C);
    fault_handler(16, 0);
}

void alignment_check(void)
{
    screen_writeln("Alignment Check", 0x0C);
    fault_handler(17, 0);
}

void machine_check(void)
{
    screen_writeln("Machine Check", 0x0C);
    fault_handler(18, 0);
}

void simd_fpu_exception(void)
{
    screen_writeln("SIMD FPU Exception", 0x0C);
    fault_handler(19, 0);
}