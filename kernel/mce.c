#include "mce.h"
#include "io.h"

void mce_handler(unsigned int mce_num, unsigned int error_code) {
    unsigned int i;
    unsigned int mce_status;
    unsigned int mce_addr;
    unsigned int mce_misc;

    // Lire les registres MCE (simplifié pour x86 32-bit)
    asm volatile("rdmsr" : "=a"(mce_status) : "c"(0x00000017) : "edx");
    asm volatile("rdmsr" : "=a"(mce_addr) : "c"(0x00000018) : "edx");
    asm volatile("rdmsr" : "=a"(mce_misc) : "c"(0x00000019) : "edx");

    // Affichage basique via ports série (simplifié)
    outb(0x3F8, 'M');
    outb(0x3F8, 'C');
    outb(0x3F8, 'E');
    outb(0x3F8, ':');
    outb(0x3F8, '0' + (mce_num / 10));
    outb(0x3F8, '0' + (mce_num % 10));

    // Arrêt du système
    while(1) {
        asm volatile("hlt");
    }
}