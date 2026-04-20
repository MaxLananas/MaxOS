#include "fault_handler.h"
#include "exceptions.h"
#include "io.h"

void fault_handler(unsigned int isr_num, unsigned int err_code) {
    outb(0x20, 0x20);
    if (isr_num >= 40) outb(0xA0, 0x20);

    switch(isr_num) {
        case 0: divide_error_handler(); break;
        case 1: overflow_handler(); break;
        case 2: non_maskable_interrupt_handler(); break;
        case 3: break_point_handler(); break;
        case 4: overflow_handler(); break;
        case 5: bound_range_handler(); break;
        case 6: invalid_opcode_handler(); break;
        case 7: device_not_available_handler(); break;
        case 8: double_fault_handler(err_code); break;
        case 9: coprocessor_segment_overrun_handler(); break;
        case 10: invalid_tss_handler(err_code); break;
        case 11: segment_not_present_handler(err_code); break;
        case 12: stack_segment_fault_handler(err_code); break;
        case 13: general_protection_fault_handler(err_code); break;
        case 14: page_fault_handler(err_code); break;
        case 16: x87_fpu_floating_point_error_handler(); break;
        case 17: alignment_check_handler(err_code); break;
        case 18: machine_check_handler(); break;
        case 19: simd_fp_exception_handler(); break;
        default:
            if (isr_num >= 32 && isr_num < 48) {
                screen_write("IRQ ");
                screen_write_hex(isr_num - 32);
                screen_write(" handled\n");
            } else {
                screen_write("Unhandled exception: ");
                screen_write_hex(isr_num);
                screen_write("\nSystem halted.\n");
                asm volatile("cli; hlt");
            }
    }
}