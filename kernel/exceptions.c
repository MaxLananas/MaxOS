#include "exceptions.h"
#include "screen.h"
#include "io.h"

void page_fault_handler(unsigned int fault_addr, unsigned int err_code) {
    screen_write("Page Fault at address: ",22);
    screen_write_hex(fault_addr);
    screen_write(" Error code: ",13);
    screen_write_hex(err_code);
    while(1);
}

void double_fault_handler(unsigned int err_code) {
    screen_write("Double Fault! Error code: ",26);
    screen_write_hex(err_code);
    while(1);
}

void nmi_handler() {
    screen_write("Non-Maskable Interrupt (NMI)!",29);
    while(1);
}

void machine_check_handler() {
    screen_write("Machine Check Exception!",25);
    while(1);
}

void general_protection_fault_handler(unsigned int err_code) {
    screen_write("General Protection Fault! Error code: ",37);
    screen_write_hex(err_code);
    while(1);
}