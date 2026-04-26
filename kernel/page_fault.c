#include "page_fault.h"
#include "fault_handler.h"

void page_fault_handler(unsigned int err) {
    fault_handler(14, err);
}