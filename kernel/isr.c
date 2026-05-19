#include "isr.h"
#include "io.h"

void isr_handler(unsigned int num, unsigned int err) {
    // Appel du fault_handler avec les bons paramètres
    fault_handler(num, err);
}